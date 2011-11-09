"""
This will house a class that will monitor a TCP connection and work out RTT etc... 
"""

import dpkt
import sys

PATH_FORWARD = 1
PATH_BACKWARD = 2

DATA_FLOAT = 1
DATA_TIMEDATE = 2

TIME_FIRST = 1
TIME_LAST = 2

def dfToFloat(td):
	"""
	Will output a float of the timedelta
	"""
	
	result = 0.0 # o.o
	result += float(td.microseconds)/1000000.
	result += float(td.seconds)
	
	
	return result
	
	


class TcpCon(object):
	def __init__(self, ip, ts):
		self.ip = ip
		self.tcp = self.ip.data
		
		#This is out socket
		self.ip1 = self.ip.src
		self.ip2 = self.ip.dst
		self.port1 = self.tcp.sport
		self.port2 = self.tcp.dport
		
		self.forward = [(ts, ip.data)]
		self.backward = []
	
	def sameSocket(self, ip):
		"""
		Will return true or false if this is the same multiplexed connection this 
		class is concerned with
		"""
		
		#Contains a TCP connection?
		if type(ip.data) != type(dpkt.tcp.TCP()):
			return False
		
		#One Way
		if (ip.src == self.ip1 and ip.data.sport == self.port1 and 
		    ip.dst == self.ip2 and ip.data.dport == self.port2):
			return True
		#Or another
		if (ip.src == self.ip2 and ip.data.sport == self.port2 and 
		    ip.dst == self.ip1 and ip.data.dport == self.port1):
			return True
		
		#I'm gonna gat ya!
		return False
		
	def addPacket(self, tcp, ts):
		"""
		This will add a packet into the list.
		"""
		if ( tcp.sport == self.port1 and tcp.dport == self.port2 ):
			#Forward
			self.forward.append((ts, tcp))
			
		if ( tcp.sport == self.port2 and tcp.dport == self.port1 ):
		    	#backward
		    	self.backward.append((ts, tcp))

	def getRTT(self, outtype=DATA_FLOAT, grabLatest=True, path=PATH_FORWARD, time=TIME_FIRST):
		"""
		This will work out the Round Trip time of 
		"""
		
		
		
		if path == PATH_FORWARD:
			ldata = self.forward
			lack = self.backward
		else:
			lack = self.forward
			ldata = self.backward
		
		#This will look through the Ack list, and find the corrisponding Data with matching sequence
		timestamp = []
		rttvals = []
		prevAcks = []
		lastack = None
		originTS = None
		for ts, ack in lack:
			#Go through each ack!
			
			#Check if ACK flag is to be paid some attention?
			if not ack.flags & dpkt.tcp.TH_ACK:
				#print "Not Ack"
				continue
			
			if lastack == None:
				#First Ack
				lastack = ack.ack
				prevAcks.append(ack.ack)
				
				print "First Ack of", lastack
				
			
			elif ack.ack in prevAcks:
				#print "Dupe acks", len(ack.data)
				prevAcks.append(ack.ack)
				continue
				pass
			else:
				#newack
				prevAcks.append(ack.ack)
				if grabLatest:
					if lastack < ack.ack:
						lastack = ack.ack
					else:
						
						continue
				else:
					lastack = ack.ack
				
				
				
			#Find ack in ldata?
			for sts, dat in ldata:
				r = (dat.seq+len(dat.data))%2**32
						
				
				if r == lastack or r+1 == lastack:
					
					if originTS == None:
						originTS = sts
					#Got it bitch!
					td = ts - sts
					
					if time == TIME_LAST:
						sts = ts
					
					if outtype == DATA_FLOAT:
						sts = dfToFloat(sts-originTS)
						td = dfToFloat(td)
						
					
					timestamp.append(sts)
					rttvals.append(td)
					
					
					break
				
		
		
				
		return (timestamp, rttvals)
					
				
	def unackdPackets(self, outtype=DATA_FLOAT):
		"""
		This will return the number of UnAcknoledged packets in a window
		"""
		
		#Will cycle through the forward path for sending packets
		#then cycle through the ack list to tick off confrimed packets
		
		lastSeq = None
		lastAck = None
		timeOrigin = None
		latestTS = None
		
		#copy the list
		forward = self.forward[:]
		backward = self.backward[:]
		
		next = None
		
		times = []
		window = []
		
		while True:
			
			if len(forward) != 0 and len(backward) != 0:
				f = forward[0]
				b = backward[0]
				
				if f[0] < b[0]:
					next = PATH_FORWARD
				else:
					next = PATH_BACKWARD
			elif len(forward) == 0 and len(backward) != 0:
				print "F Empty"
				next = PATH_BACKWARD
			elif len(backward) == 0 and len(forward) != 0:
				print "B Empty"
				next = PATH_FORWARD
			else:
				#both are zero, BREAK
				print "Both Empty"
				break
			noSeqYet = False
			if next == PATH_FORWARD:
				#add onto the path forward
				ts, dat = forward[0]
				if lastSeq == None:
					lastSeq = dat.seq+len(dat.data)
					lastAck = dat.seq
					timeOrigin = ts
					
				
				elif lastSeq < dat.seq:
					lastSeq = dat.seq+len(dat.data)
				
				forward = forward[1:]
				
			else:
				#add onto backward path!
				ts, dat = backward[0]
				
				if lastAck == None:
					noSeqYet = True
				elif dat.ack > lastAck:
					lastAck = dat.ack
				
				backward = backward[1:]
			
			if noSeqYet:
				continue
			
			dif = lastSeq - lastAck
			td = ts - timeOrigin
			if outtype == DATA_FLOAT:
				td = dfToFloat(td)
			
			times.append(td)
			window.append(dif)
			
		return (times, window)
					
					
				
	def workRate(self, path=PATH_FORWARD, window=4, limit=1*10**6):
		"""
		this will try to work out the rate at which we are Tx/Rx packets
		path = tx or rx
		window = moving point average/ish (move like convoultion but in the packet values, not time)
		"""
		
		if path == PATH_FORWARD:
			pkts = self.forward
		elif path == PATH_BACKWARD:
			pkts = self.backward
		else:
			return None
			
		origin = pkts[0][0]
		
		speeds = []
		resultts = []
		for x in xrange(1, len(pkts)+window):
			start = x-window
			end = x
			
			if start < 0:
				start = 0
			if end >= len(pkts):
				end = len(pkts)-1
				
			
			
			pktwindow = pkts[start:end]
			if len(pktwindow) < 2:
				continue
			#sum data
			s = 0
			for ts, dat in pktwindow[1:]:
				s += len(dat)
				
			td = pktwindow[-1][0] - pktwindow[0][0]
			try:
				speed = s/dfToFloat(td)
			except:
				#division by zero? :o
				continue
			if speed > limit:
				speed=limit
			speeds.append(speed)
			ts = dfToFloat(pktwindow[-1][0] - origin)
			resultts.append(ts)
		
		return resultts, speeds
		
				
			
		
					
				
		
				
			
