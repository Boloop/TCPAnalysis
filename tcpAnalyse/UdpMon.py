"""
This is the simpleSend Monitor for the connection, just like you have 
tcpmon!
"""

import TcpMon
import dpkt
import SSPack


PATH_FORWARD = 1
PATH_BACKWARD = 2

DATA_FLOAT = 1
DATA_TIMEDATE = 2

TIME_FIRST = 1
TIME_LAST = 2

RELATIVE_ABSOLUTE = 1
RELATIVE_LASTACK = 2

ECN_NONECT = 0
ECN_ECT0 = 2
ECN_ECT1 = 1
ECN_CE = 3

class UdpCon(object):
	def __init__(self, ip, ts):
		self.ip = ip
		self.udp = ip.data
		
		self.ip1 = self.ip.src
		self.ip2 = self.ip.dst
		self.port1 = self.udp.sport
		self.port2 = self.udp.dport
		
		dp = ip.data
		udp = ip.data
		#print "len, UDP", len(ip.data.data)
		#HACK?
		sp = SSPack.SSPack()
		try:
		#if True:
			sp.read(ip.data.data)
		except:
			print "SSPack failed to Read :o"
			return
		sp.sport = udp.sport
		sp.dport = udp.dport
		udp = sp
		
		self.forward = [(ts, udp)]
		self.backward = []
		
		self.forwardECN = [ ( ts, TcpMon.getECNFlagsFromIP ( ip.pack_hdr() ) ) ]
		self.backwardECN = []
		
		self.origin = None
		
	def setOrigin(self):
		"""
		This will set up the time origin, be the easiliest of the two first packets
		in the forward and backward lists
		"""
		
		
		self.origin = self.forward[0][0]
		
		if self.origin > self.backward[0][0]:
			self.origin = self.backward[0][0]
	
	def sameSocket(self, ip):
		"""
		Will return true or false if this is the same multiplexed connection this 
		class is concerned with
		"""
		
		#Contains a TCP connection?
		if type(ip.data) != type(dpkt.udp.UDP()):
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
	
	
	def addIPPacket(self, ip, ts):
		"""
		this will add the ip packet into the list
		"""
		udp = ip.data
		print "len, UDP", len(udp.data)
		#HACK?
		sp = SSPack.SSPack()
		try:
			sp.read(udp.data)
		except:
			print "SSPack failed to Read"
			return
		sp.sport = udp.sport
		sp.dport = udp.dport
		udp = sp
		#print type(udp), type(sp)
		
		if ( udp.sport == self.port1 and udp.dport == self.port2 ):
			#Forward
			self.forward.append((ts, sp))
			self.forwardECN.append( ( ts, TcpMon.getECNFlagsFromIP ( ip.pack_hdr() ) ) )
			
		if ( udp.sport == self.port2 and udp.dport == self.port1 ):
		    	#backward
		    	self.backward.append((ts, sp))
		    	self.backwardECN.append( ( ts, TcpMon.getECNFlagsFromIP ( ip.pack_hdr() ) ) )
	
	def addPacket(self, udp, ts):
		"""
		This will add a packet into the list.
		"""
		if ( udp.sport == self.port1 and udp.dport == self.port2 ):
			#Forward
			self.forward.append((ts, udp))
			
		if ( udp.sport == self.port2 and udp.dport == self.port1 ):
		    	#backward
		    	self.backward.append((ts, udp))
	
	def getHandshake(self):
		"""
		This will return (SYN, SYNACK, ACK)
		THERE IS NO HANDSHAKE IN THE UDP 
		"""
		
		print "No handshake!"
		raise ZeroDivisionError
	
	def getPacketCount(self):
		"""
		Will return the number of packets held for this connection
		"""
		
		return len(self.forward)+len(self.backward)
	
	def removeFIN(self):
		"""
		Does nothing, no Handshake to remove
		"""
		return
	
	def getTXRate(self, path=PATH_FORWARD):
		"""
		Will return tuple for Datasent, and td of first and last data sent
		"""
	
	
		if path == PATH_FORWARD:
			segs = self.forward
			acks = self.backward
		else:
			segs = self.backward
			acks = self.forward
		
		fts = None
		lts = None
		fseq = None
		lseq = None
		tdata = None
		
		for ts, p in segs:
			if len(p.payload) == 0:
				continue
			
			if fseq == None:
				print type(p)
				fseq = p.segNo
				fts =  ts
			
				lseq = fseq
				lts = fts
				tdata = len(p.payload)
			
			if p.segNo > lseq:
				lseq = p.segNo
				tdata += len(p.payload)
				lts = ts
		
		return tdata, TcpMon.dfToFloat(lts-fts)
		
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
		
		times = [0]
		window = [0]
		
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
					lastSeq = dat.segNo*1400+len(dat.payload)
					lastAck = dat.segNo*1400
					timeOrigin = self.origin
					
				
				elif lastSeq < dat.segNo*1400:
					lastSeq = dat.segNo*1400+len(dat.payload)
				
				forward = forward[1:]
				
			else:
				#add onto backward path!
				ts, dat = backward[0]
				
				if lastAck == None:
					noSeqYet = True
				elif dat.ackNo*1400 > lastAck:
					lastAck = dat.ackNo*1400
				
				backward = backward[1:]
			
			if noSeqYet:
				continue
			
			dif = lastSeq - lastAck
			td = ts - timeOrigin
			if outtype == DATA_FLOAT:
				td = TcpMon.dfToFloat(td)
			
			times.append(td)
			window.append(dif)
		
		#add last
		times.append(times[-1]*2.01)
		window.append(1)
		print "Added last?"
		print times[-1], window[-1]
		return (times, window)
		
	def getRetransmits(self, outtype=DATA_FLOAT, path=PATH_FORWARD, rel=RELATIVE_LASTACK):
		"""
		This will return a (ts, segmentnumber, len?)
		"""
		
		timestamps = []
		segments = []
		lengths = []
		
		if path == PATH_FORWARD:
			segs = self.forward
			acks = self.backward
		else:
			segs = self.backward
			acks = self.forward
		
		lastSeg = None
		origin = None
		previousHaveData = None
		
		for ts, dat in segs:
			if lastSeg == None:
				lastSeg = dat.segNo*1400
				origin = ts
				previousHaveData = len(dat.payload)
				continue
			
			
			
			if lastSeg <= dat.segNo*1400:
				lastSeg = dat.segNo*1400
				continue
			
			#Before!
			if len(dat.payload) == 0:
				#print "Found DUPE (nodata)", dat.seq, dat.flags
				continue
			
			#print "Found DUPE", dat.seq, dat.flags
			timestamps.append(ts)
			segments.append(dat.segNo*1400)
			#lengths.append(len(dat))
			lengths.append(500)
		
		
		if rel == RELATIVE_ABSOLUTE:
			pass
		elif rel == RELATIVE_LASTACK:
			#The last ackknowledgement
			lastack = None
			lastackTS = None
			isegs = 0
			iacks = 0
			newsegs = []
			oldlen = len(segments)
			#print "seggy len before", len(segments), segments
			for seg in segments:
				
				
				#find ack to it
				while iacks < len(acks):
					tsa, p = acks[iacks]
					if tsa > timestamps[isegs]:
						#just past it, check one before!
						newsegs.append(seg-lastack)
						break
					lastack = p.ackNo*1400
					iacks += 1
				isegs += 1
			
			segments = newsegs
			while oldlen != len(segments):
				segments.append(0)
			
			#print "seggy len after", len(segments), segments			
				
				
		
		if outtype == DATA_FLOAT:
			newts = []
			for x in timestamps:
				ts = x-origin
				x = TcpMon.dfToFloat(ts)
				newts.append(x)
			timestamps = newts		
					
		
		
		return timestamps, segments, lengths
	
				
	
	def getSACKs(self, outtype=DATA_FLOAT, path=PATH_BACKWARD, rel=RELATIVE_LASTACK):
		"""
		This will return a list of SACKs of when and what?
		
		(ts, ack, (segs,))
		"""
		
		sackpacks = []
		
		if path == PATH_BACKWARD:
			pkts = self.backward
		else:
			pkts = self.forward
		
		for ts, p in pkts:
			if outtype == DATA_FLOAT:
				ts = ts-self.origin
				ts = TcpMon.dfToFloat(ts)
			
			#opts = TCPOptions(p.opts)
			
			if len(p.ackList) > 0:
				
				if rel == RELATIVE_LASTACK:
					nsegs = []
					for s in p.ackList:
						nsegs.append(s-p.ackNo)
					#print "ts,ack", ts, p.ack
					#print "oldsegs", segs
					#print "newsegs", nsegs
					segs = tuple(nsegs)
				
				sackpacks.append( (ts, p.ackNo, segs) )
		
		return sackpacks
		
	def countFlags(self, flag, path=PATH_BACKWARD):
		"""
		This will count the number of ECE flagged packets
		SSPack doesn't Echo ECN bits... REturns -1
		"""
		
			
		return -1
		
	def countECNInIP(self, flag=ECN_CE, path=PATH_BACKWARD):
		"""
		Will return the number of packets of ecn in IP
		SSPack doesn't Echo ECN bits... REturns -1
		"""	
		
		return -1
