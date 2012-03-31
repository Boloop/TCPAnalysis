import time

PHASE_SLOWSTART = 1
PHASE_CONGESTIONAVOIDANCE = 2
PHASE_FASTRETRANSMIT = 3
PHASE_FASTRECOVERY = 4

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
		
	def onAck(self, pack):
		"""
		First method called on getting A packet back, This will just
		care for only the Acknowedgement numbers for data that was sent.
		"""
		
		#Recalculate RTT?
		self.recalcRTTonPack(pack)
		
		#Tick off Packets
		ackdAmount = self.ackPackets(pack)
		
		#Got a TrippleDupe Ack?
		dupeAck = False
		if pack.ackNo == self.lastAck:
			self.duplicateAckCount += 1
			dupeAck = True
		else:
			self.duplicateAckCount = 0
		
		if self.duplicateAckCount >= 3:
			#TDDAck Detected, Have we already encountered one in the past RTT?
			if self.lastTDATS + self.RTTavg < time.time():
				#new TDA event
				self.tdaEvent()
		
		partialAck = len(pack.ackList) != 0
		
		#Send a new segment (or Two?)
		self.sendNewData(dupeAck=dupeAck, ackdAmount=ackdAmount, partialAck=partialAck)
	
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
			self.lastCongIncrease = time.time()
			
		elif self.congPhase == PHASE_CONGESTIONAVOIDANCE:
			if self.lastCongIncrease + self.RTTavg < time.time():
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
			self.onWire[sindex] = (self.onWire[sindex][0], time.time(), self.onWire[sindex][2])
			
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
				self.lastCongIncrease = time.time()
				
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
		
		#Space to retransmit new data?
		if newDataToSend == None and len(self.onWire) < self.congWin:
			#Grab new data
			newdata = "\x00"*1400
			nseg = self.newSegNum
			self.newSegNum += 1
			self.onWire.append( (nsg, time.time(), newdata) )
			newDataToSend = (nsg ,newdata)
	
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
		echodTS = pack.lastDestinationTS
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
		#For upto and including the pack.lastAck
		for sn, ts, payload in self.onWire:
			if sn <= pack.ackNo:
				rml.append((sn, ts, payload))
			elif sn in pack.ackList:
				rml.append((sn, ts, payload))
		
		#Got removal list
		for r in rml:
			self.onWire.remove(r)
			
		return len(rml)
		
