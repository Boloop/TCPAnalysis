import time
import SSPack
import math

PHASE_SLOWSTART = 1
PHASE_CONGESTIONAVOIDANCE = 2
PHASE_FASTRETRANSMIT = 3
PHASE_FASTRECOVERY = 4

phaseToText = {
	PHASE_SLOWSTART:"SlowStart",
	PHASE_CONGESTIONAVOIDANCE : "Congestion Avoidance",
	PHASE_FASTRETRANSMIT : "Fast Retransmit",
	PHASE_FASTRECOVERY : "Fast Recovery"
}

class SSSender():
	
	def __init__(self):
		self.lastAck = -1 
		self.newSegNum = 0
		self.lastAckTS = 0 #The timestamp of the last ACK recieved?
		self.duplicateAckCount = 0 
		self.lastTDATS = 0
		self.onWire = [] # List of packet Numbers sent that are unack'd
		
		self.RTTavg = None
		self.RTTdev = None
		
		self.congWin = 1
		self.congPhase = PHASE_SLOWSTART
		self.lastCongIncrease = 0
		self.ssThreshold = 1000
		self.fastRecoveryRetransmitNo = 0
		
		self.sendCall = None
		self.timeNow = time.time # This is to overide for testing...
		
	def __str__(self):
		"""
		
		"""
		s = "oW: "+str(len(self.onWire))+" CongWin: "+str(self.congWin)+" CongPhase: "+phaseToText[self.congPhase]
		s += " ssThres: "+str(self.ssThreshold)+" RTTa:"+str(self.RTTavg)
		
		return s
		
	def onAck(self, pack):
		"""
		First method called on getting A packet back, This will just
		care for only the Acknowedgement numbers for data that was sent.
		"""
		
		#Recalculate RTT?
		self.recalcRTTonPack(pack)
		
		
		
		#Got a TrippleDupe Ack?
		dupeAck = False
		print "this Ack,",pack.ackNo, "lastAck", self.lastAck
		if pack.ackNo == self.lastAck:
			self.duplicateAckCount += 1
			dupeAck = True
		else:
			self.duplicateAckCount = 0
			
		#Tick off Packets - goes *AFTER* checking for dupe (this changes self.lastAck)
		ackdAmount = self.ackPackets(pack)
		
		if self.duplicateAckCount >= 3:
			#TDDAck Detected, Have we already encountered one in the past RTT?
			if self.lastTDATS + self.RTTavg < self.timeNow():
				#new TDA event
				self.tdaEvent()
		
		partialAck = len(pack.ackList) != 0
		
		print "onAck - AckNo:"+str(pack.ackNo)+ " Acked:"+str(ackdAmount)+" dupeAck:"+str(dupeAck)
		
		#Send a new segment (or Two?)
		self.sendNewData(dupeAck=dupeAck, ackdAmount=ackdAmount, partialAck=partialAck)
	
	def segsOnWire(self):
		"""
		Will return list of Segs on wire
		"""
		
		result = []
		for sn, ts, payload in self.onWire:
			result.append(sn)
			
		return result
	
	def sendNewData(self, dupeAck=False, ackdAmount=1, partialAck=False):
		"""
		On an Ack we can send more Data, This will increase our congestion window...
		AND send data to ensure data on the wire matches that
		"""
		#
		#Congestion Increase?
		#
		
		if self.congPhase == PHASE_SLOWSTART:
			self.congWin += 1
			self.lastCongIncrease = self.timeNow()
			
		elif self.congPhase == PHASE_CONGESTIONAVOIDANCE:
			if self.lastCongIncrease + self.RTTavg < self.timeNow():
				self.congWin += 1
				self.lastCongIncrease += self.RTTavg
				
		elif self.congPhase == PHASE_FASTRETRANSMIT:
			self.congWin = self.ssThreshold + 3 # Artificial inflation from TDA
			
		elif self.congPhase == PHASE_FASTRECOVERY:
			self.congWin += 1
			
		#
		#Transmit New Packet
		#
		
		newDataToSend = None
		
		if self.congPhase == PHASE_FASTRETRANSMIT:
			#Get smallest data segment, that is our missing segment
			smallest = None
			index = 0
			sindex = 0
			for sn, ts, payload in self.onWire:
				if smallest == None:
					smallest = sn
					sindex = index
				elif sn < smallest:
					smallest = sn
					sindex = index
				index += 1
			#Got smallest index
			newDataToSend = (self.onWire[sindex][0], self.onWire[sindex][2])
			#update TS
			self.onWire[sindex] = (self.onWire[sindex][0], self.timeNow(), self.onWire[sindex][2])
			
			self.fastRecoveryRetransmitNo = newDataToSend[0]
			self.congPhase = PHASE_FASTRECOVERY
			
		elif self.congPhase == PHASE_FASTRECOVERY:
			#Check if we have acknowledged fast recovery packet
			hasAckd = True # True if not in list
			for sn, ts, payload in self.onWire:
				if sn == self.fastRecoveryRetransmitNo:
					hasAckd = False
					break
			
			if hasAckd and not partialAck:
				#Break out of FastRECOVERY!
				
				#Delfate Window
				ncong = self.ssThreshold
				if ncong > (len(self.onWire)+1):
					ncong = len(self.onWire)+1
				
				self.congWin = ncong
				self.lastCongIncrease = self.timeNow()
				
				self.congPhase = PHASE_CONGESTIONAVOIDANCE
			elif partialAck:
				#deflate the window... This is RFC2582 Section 3 point 5.
				ncong = self.congWin - ackdAmount + 1
				if ncong < 1:
					ncong = 2
				self.congWin = ncong
				
				#retransmit.
				
				
			
			# Can Never EVER get Not Acking the missing data "AND" not a partial ack
			# In Theory, unless something bad is happening.
		
		
		#Transmit new data
		if newDataToSend != None:
			p = SSPack.SSPack()
			p.segNo, p.payload = newDataToSend
			self.sendPacket(p)
		
		
		#Space to retransmit new data?
		while len(self.onWire) < self.congWin:
			#Grab new data
			newdata = "\x00"*1400
			nseg = self.newSegNum
			self.newSegNum += 1
			self.onWire.append( (nseg, self.timeNow(), newdata) )
			newDataToSend = (nseg ,newdata)
			
			p = SSPack.SSPack()
			p.segNo, p.payload = newDataToSend
			self.sendPacket(p)
	
	def getFirstUnAckdPacket(self, updateTS=None):
		#Get smallest data segment, that is our missing segment
		result = None
		smallest = None
		index = 0
		sindex = 0
		for sn, ts, payload in self.onWire:
			if smallest == None:
				smallest = sn
				sindex = index
			elif sn < smallest:
				smallest = sn
				sindex = index
			index += 1
		#Got smallest index
		result = (self.onWire[sindex][0], self.onWire[sindex][2])
		#update TS
		if updateTS != None:
			self.onWire[sindex] = (self.onWire[sindex][0], updateTS, self.onWire[sindex][2])
	
		
	def tdaEvent(self):
		"""
		Action to be taken under a TDA event
		"""
		if self.congPhase == PHASE_FASTRECOVERY:
			return
		
		self.congPhase = PHASE_FASTRETRANSMIT
		
		#Calculate new Threshold!
		nth = len(self.onWire)/2
		if nth < 2:
			nth = 2
		
		self.ssThreshold = nth
		pass
	
	def recalcRTTonPack(self, pack):
		"""
		With new echo'd TS will recalculate the new RTT
		"""
		echodTS = self.timeNow() - pack.lastDestinationTS
		if self.RTTavg == None:
			self.RTTavg = echodTS 
			self.RTTdev = 0
		else:
			self.RTTavg = self.RTTavg*0.9 + echodTS*0.1
			self.RTTdev = self.RTTdev*0.9 + 0.1*math.fabs(self.RTTavg - echodTS)
			
	def ackPackets(self, pack):
		"""
		Will read in the Ack numbers and tick off all packets passed sucesfully
		Will return number of packets that have been "ticked off"
		"""
		
		rml = []
		smallest = None # For lastAck
		#For upto and including the pack.lastAck
		for sn, ts, payload in self.onWire:
			if sn <= pack.ackNo:
				rml.append((sn, ts, payload))
			elif sn in pack.ackList:
				rml.append((sn, ts, payload))
			else:
				
				if smallest == None:
					smallest = sn
				elif sn < smallest:
					smallest = sn
		
		#Got removal list
		for r in rml:
			self.onWire.remove(r)
		
		#Get smallest in ackPackets and set lastAck as -1
		if smallest != None:
			self.lastAck = smallest - 1
			 
		return len(rml)
	
	def sendPacket(self, pack):
		"""
		This is a PRIVATE method, called internally to send the call send method
		"""
		
		self.sendCall(pack)
		
	def sendOnIdle(self, pack=None):
		"""
		Test, to send first packet!
		"""
		p = SSPack.SSPack()
		data = "\x00"*1400
		p.payload = data
		p.segNo = self.newSegNum
		n = (self.newSegNum, self.timeNow(), data)
		self.onWire.append(n)
		self.newSegNum += 1
		self.sendPacket(p)
		
		
		
		
