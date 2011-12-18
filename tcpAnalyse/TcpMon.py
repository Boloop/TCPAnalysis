"""
This will house a class that will monitor a TCP connection and work out RTT etc... 
"""

import dpkt
import sys
import struct

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



optsToString = {dpkt.tcp.TCP_OPT_ALTSUM		:"ALTSUM",
		dpkt.tcp.TCP_OPT_BUBBA		:"BUBBA",
		dpkt.tcp.TCP_OPT_CC		:"CC",
		dpkt.tcp.TCP_OPT_CCECHO		:"CCECHO",
		dpkt.tcp.TCP_OPT_CCNEW		:"CCNEW",
		dpkt.tcp.TCP_OPT_CORRUPT	:"CORRUPT",
		dpkt.tcp.TCP_OPT_ECHO		:"ECHO",
		dpkt.tcp.TCP_OPT_ECHOREPLY	:"ECHOREPLY",
		dpkt.tcp.TCP_OPT_EOL		:"EOL",
		dpkt.tcp.TCP_OPT_MAX		:"MAX",
		dpkt.tcp.TCP_OPT_MD5		:"MD5",
		dpkt.tcp.TCP_OPT_MSS		:"MSS",
		dpkt.tcp.TCP_OPT_NOP		:"NOP",
		dpkt.tcp.TCP_OPT_POCONN		:"POCONN",
		dpkt.tcp.TCP_OPT_POSVC		:"POSVC",
		dpkt.tcp.TCP_OPT_REC		:"REC",
		dpkt.tcp.TCP_OPT_SACK		:"SACK",
		dpkt.tcp.TCP_OPT_SACKOK		:"SACKOK",
		dpkt.tcp.TCP_OPT_SCPS		:"SCPS",
		dpkt.tcp.TCP_OPT_SKEETER	:"SKEETER",
		dpkt.tcp.TCP_OPT_SNACK		:"SNACK",
		dpkt.tcp.TCP_OPT_SNAP		:"SNAP",
		dpkt.tcp.TCP_OPT_TCPCOMP	:"TCPCOMP",
		dpkt.tcp.TCP_OPT_TIMESTAMP	:"TIMESTAMP",
		dpkt.tcp.TCP_OPT_TRAILSUM	:"TRAILSUM",
		dpkt.tcp.TCP_OPT_WSCALE		:"WSCALE",}


def dfToFloat(td):
	"""
	Will output a float of the timedelta
	"""
	
	result = 0.0 # o.o
	result += float(td.microseconds)/1000000.
	result += float(td.seconds)
	
	
	return result

hexStrDic = {0:"0", 1:"1", 2:"2", 3:"3", 4:"4", 5:"5", 6:"6", 7:"7", 8:"8", 9:"9", 10:"A", 11:"B", 12:"C", 13:"D", 14:"E", 15:"F"}

def hexStr(s):
	result = ""
	for x in s:
		x = ord(x)
		a = x/16
		b = x%16
		
		result += "0x" + hexStrDic[a] + hexStrDic[b]
	return result
		
def parseOption(n, d):
	"""
	This will convert the data part for option to something we like a little better,
	like intergets and datetime formats! :)
	"""	
	
	if n == dpkt.tcp.TCP_OPT_WSCALE:
		return 2**struct.unpack("B", d)[0]
	
	if n == dpkt.tcp.TCP_OPT_MSS:
		return struct.unpack(">H", d)[0]
	if n == dpkt.tcp.TCP_OPT_TIMESTAMP:
		a, b = struct.unpack(">II", d)
		return (a*0.01, b*0.01)
	
	if n == dpkt.tcp.TCP_OPT_SACK:
		#can be variable lengh
		res = []
		for i in xrange(0, len(d)/4):
			a = struct.unpack(">I", d[4*i:4*i+4])[0]
			#print "where a", a, "from", hexStr(d[i:i+4])
			res.append(a)
		
		#print "This:"+hexStr(d)+ "to " + str(res)
		return tuple(res)
	
	return None
	


class TCPOptions(object):
	"""
	It seems the dkpt library doesn't put the tcp opts in their own class, it has a few flags, and a parsing
	function, but very limited. This will hopefully automate common tasks
	"""
	
	def __init__(self, data=None):
		self.options = []
		
		
		if type(data) == type(""):
			data = dpkt.tcp.parse_opts(data)
			#print data
		for n, d in data:
			d = parseOption(n, d)
			self.options.append( (n, d) )
		
		#self.options = data
	
	def __str__(self):
		s = "["
		for n, x in self.options:
			s += " "+optsToString[n]+":"+str(x)+", "
		
		s += "]"
		
		return s
	
	def get(self, opt, index=0):
		"""
		This will get data for an option in the list
		"""
		i = 0
		for n, d in self.options:
			if n == opt:
				if i == index:
					return d
				i += 1
		return None
	
	def __contains__(self,opt):
		"""
		Will see if an option is in
		"""
		for n, d in self.options:
			if n == opt:
				return True
		return False
		
		
				
def getECNFlagsFromIP(ipHeader):
	"""
	give in ip.pack_hdr() and this will read the magical number and return 
	the ECN value.
	"""
	val = ord(ipHeader[2]) & 3 # last two bits of the 3rd byte
	
	#ECN_NONECT = 0
	#ECN_ECT0 = 2
	#ECN_ECT1 = 1
	#ECN_CE = 3
	
	
	if val == 0: return ECN_NONECT
	if val == 2: return ECN_ECT0
	if val == 1: return ECN_ECT1
	if val == 3: return ECN_CE
	
	return None
	

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
		
		self.forwardECN = [ ( ts, getECNFlagsFromIP ( ip.pack_hdr() ) ) ]
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
		
	
	def addIPPacket(self, ip, ts):
		"""
		this will add the ip packet into the list
		"""
		tcp = ip.data
		
		if ( tcp.sport == self.port1 and tcp.dport == self.port2 ):
			#Forward
			self.forward.append((ts, tcp))
			self.forwardECN.append( ( ts, getECNFlagsFromIP ( ip.pack_hdr() ) ) )
			
		if ( tcp.sport == self.port2 and tcp.dport == self.port1 ):
		    	#backward
		    	self.backward.append((ts, tcp))
		    	self.backwardECN.append( ( ts, getECNFlagsFromIP ( ip.pack_hdr() ) ) )
	
	
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
		    	
	def getHandshake(self):
		"""
		This will return (SYN, SYNACK, ACK)
		"""
		
		#First packet must be a Syn
		tsf = self.forward[0][0]
		tsb = self.backward[0][0]
		
		if   tsf < tsb:
			synin = PATH_FORWARD
		elif tsf > tsb:
			synin = PATH_BACKWARD
		else:
			print "forward and backward start timestamps are the same? *ouch headache*"
			return None, None, None
		
		if synin == PATH_FORWARD:
			synpk = self.forward
			ackpk = self.backward
		else:
			synpk = self.backward
			ackpk = self.forward
		
		syn = None
		synack = None
		ack = None
		
		
		#Look for Syn, ACK in synpk (forward usually) list
		for ts, p in synpk:
			
			if p.flags & dpkt.tcp.TH_SYN and not p.flags & dpkt.tcp.TH_ACK:
				#is Syn
				syn = (ts, p)
			elif p.flags & dpkt.tcp.TH_ACK and not p.flags & dpkt.tcp.TH_SYN:
				#first ACK
				ack = (ts, p)
				break
		
		#Look for SynACK in ackpk (backward usually) list
		for ts, p in ackpk:
		
			if p.flags & dpkt.tcp.TH_ACK and p.flags & dpkt.tcp.TH_SYN:
				synack = (ts, p)
				break
		
		return syn, synack, ack
		
				
				
		
	def getPacketCount(self):
		"""
		Will return the number of packets held for this connection
		"""
		
		return len(self.forward)+len(self.backward)

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
						originTS = self.origin
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
	
	def getRTTbyTS(self, outtype=DATA_FLOAT, path=PATH_FORWARD):
		"""
		This will use the timestamps (if there) to work out the round trip time
		this should hopefully get around the dup ack/retransmit problem
		"""
		
		if path == PATH_FORWARD:
			ldata = self.forward
			lack = self.backward
		else:
			lack = self.forward
			ldata = self.backward
		
		rtt = []
		times = []
		
		lastsentTS = None # float of TCP ts
		lastsentTSsent = None #datetime of pcap TS
		i = 0
		for ts, p in lack:
			#Grab the timestamp!
			
			
			opts = TCPOptions(p.opts)
			pktts = opts.get(dpkt.tcp.TCP_OPT_TIMESTAMP)
			
			if pktts == None:
				print "Na1"
				continue
			
			if lastsentTS == None:
				lastsentTS = pktts[1]
				lastsentTSsent = ts
				continue
			
			if lastsentTS > pktts[1]:
				print "hey"
				continue
			lastsentTS = pktts[1]
			lastsentTSsent = ts
			
			#for each one find corrisponding one?
			
			while i < len(ldata):
				
				tss, ps = ldata[i]
				
				optss = TCPOptions(ps.opts)
				pkttss = optss.get(dpkt.tcp.TCP_OPT_TIMESTAMP)
				
				if pkttss == None:
					print "Na2", i
					i += 1
					continue
				if pkttss[0] < pktts[1]:
					i += 1
					continue
				
				td = ts - tss # Pcap of sent+echo TS dif
				time = ts - self.origin #pcap to origin
				if outtype == DATA_FLOAT:
						
						time = dfToFloat(time)
				print "Added", i
				rtt.append(dfToFloat(td))
				times.append(time)
				
				break
			
			
			if i >= len(ldata):
				print "Empty!"
				break
		print type(times[0]), type(rtt[0])
		return times, rtt
			
			
			
			
			
				
			
				
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
					lastSeq = dat.seq+len(dat.data)
					lastAck = dat.seq
					timeOrigin = self.origin
					
				
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
		
		#add last
		times.append(times[-1]*2.01)
		window.append(1)
		print "Added last?"
		print times[-1], window[-1]
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
			
		origin = self.origin
		
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
			if len(p.data) == 0:
				continue
			
			if fseq == None:
				fseq = p.seq
				fts =  ts
			
				lseq = fseq
				lts = fts
				tdata = len(p.data)
			
			if p.seq > lseq:
				lseq = p.seq
				tdata += len(p.data)
				lts = ts
		
		return tdata, dfToFloat(lts-fts)
				
							
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
				lastSeg = dat.seq
				origin = ts
				previousHaveData = len(dat.data)
				continue
			
			
			
			if lastSeg <= dat.seq:
				lastSeg = dat.seq
				continue
			
			#Before!
			if len(dat.data) == 0:
				#print "Found DUPE (nodata)", dat.seq, dat.flags
				continue
			
			#print "Found DUPE", dat.seq, dat.flags
			timestamps.append(ts)
			segments.append(dat.seq)
			lengths.append(len(dat))
		
		
		
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
					lastack = p.ack
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
				x = dfToFloat(ts)
				newts.append(x)
			timestamps = newts		
					
		
		
		return timestamps, segments, lengths
	
	def countFlags(self, flag, path=PATH_BACKWARD):
		"""
		This will count the number of ECE flagged packets
		"""
		
		if path == PATH_BACKWARD:
			pkts = self.backward
		else:
			pkts = self.forward
		
		count = 0
		for ts, p in pkts:
			if p.flags & flag:
				count += 1
		
		return count
	
	def removeFIN(self):
		"""
		This will remove the fin handshakes in both paths
		"""
		
		for l in [self.forward, self.backward]:
			rml = []
			i = 0
			for ts, p in l:
				if p.flags & dpkt.tcp.TH_FIN:
					#it has
					rml.append(i)
				i += 1
			
			#remove
			rml.reverse()
			print rml, "remove", len(l)
			for rm in rml:
				l.pop(rm)
	
	
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
				ts = dfToFloat(ts)
			
			opts = TCPOptions(p.opts)
			
			if dpkt.tcp.TCP_OPT_SACK in opts:
				segs =  opts.get(dpkt.tcp.TCP_OPT_SACK)
				if rel == RELATIVE_LASTACK:
					nsegs = []
					for s in segs:
						nsegs.append(s-p.ack)
					#print "ts,ack", ts, p.ack
					#print "oldsegs", segs
					#print "newsegs", nsegs
					segs = tuple(nsegs)
				
				sackpacks.append( (ts, p.ack, segs) )
		
		return sackpacks
		
					
	def countECNInIP(self, flag=ECN_CE, path=PATH_BACKWARD):
		"""
		Will return the number of packets of ecn in IP
		"""		
		
		if path == PATH_FORWARD:
			ecns = self.forwardECN
		else:
			ecns = self.backwardECN
		
		count = 0
		
		for ts, ecn in ecns:
			if ecn == flag:
				count += 1
		
		return count
			
		
				
			
