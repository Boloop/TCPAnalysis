#
#
#

import NSPack
import random
import threading
import time

STATE_NONE = 0
STATE_SYNACK = 1
STATE_CONNECTED = 2

CONG_SLOWSTART = 1



class RetransmitTimer(threading.Thread):
	def __init__(self, data, datalock, client):
		threading.Thread.__init__(self)
		self.data = data
		self.datalock = datalock
		self.client = client
		
		#self.sendsoc = sendsoc
		
		self.rtt = 100
		self.tov = 1.4 # 40% out of the RTT before it timesout!
		self.maxRT = 4
		
		self.isDead = False
		self.hasTimedOut = False
		
		self.lrt = 0
		
		self.congMSS = 1 # Redundancy FTL, :(
		
	def timeOutTime(self):
		#print self.rtt, self.tov, (self.rtt*self.tov)
		return (self.rtt*self.tov)*(2**self.lrt)
	
	def run(self):
		
		to = 1
		self.lrt = 0
		lsn = -1
		
		while 1:
			if self.isDead:
				break
			
			self.datalock.acquire()
			
			self.datalock.wait(to)
			
			#Check for data
			#print "RTimer, Sendbuff", self.data
			#print "Timer, checking for send data"
			if len(self.data) == 0:
				self.datalock.release()
				to = 1
				#print "Timer, No data :("
				continue
			
			#print "There is data! :)"
			s, d, ts = self.data[0]
			#print "S;", s, "d", d, "ts:", ts
			tot = self.timeOutTime()
			
			if ts == None:
				#print "new!"
				#Not even sent, let's send it Boys!
				self.data[0] = (s, d, time.time())
				self.client.sendWithData(d,s)
				to = tot
				if to > 1:
					to = 1
				
				
			
			else:
				#Still waiting for this one to be recieved.
				td = time.time() - ts
				print "td", td, "tot",tot
				#time.sleep(1)
				if td > tot:
					#Timed out, RT
					self.lrt += 1
					
					
					if self.lrt > self.maxRT:
						print "MAxed out?"
						self.hasTimedOut = True
						break
					else:
						#Retransmit, update sentTS
						self.client.onTimeout()
						self.data[0] = (s, d, time.time())
						self.client.sendWithData(d,s)
						
						
						#self.sendsoc()
				else:
					#Not timed out, let's sleep until it happens
					to = tot-td
					if to > 1:
						to = 1
					
					
			
			if True:
					#Check if we need to send any more packets?
					wirecount = 0
					for s, d, ts in self.data:
						if ts != None:
							wirecount += 1
						else:
							break
					
					print "NSConn Wirecount",wirecount
					if wirecount < self.congMSS:
						print "Send more!"
						
						#Send each new one
						for x in range(self.congMSS-wirecount, len(self.data)):
							s, d, ts = self.data[x]
							"Cong, extra Sending seg", s 
							self.data[x] = (s, d, time.time())
							self.client.sendWithData(d,s)
					else:
						print "No do not send! D:"
			
			
			
			if s != lsn:
				print "reset lrt"
				self.lrt = 0
				lsn = s
					
			self.datalock.release()
		
					
	



class NSConnection(object):

	def __init__(self):
		pass
		self.connid = None
		self.dip = None
		self.dport = None
		self.sip = None
		self.state = STATE_NONE
		self.sendsoc = None
		self.ipport = None
		
		self.ackn = None
		
		self.rcvBuffSize = 2048
		self.rcvBuff = []
		self.rcvLock = threading.Condition()
		
		self.sendBuff = []
		self.sendLock = threading.Condition()
		self.sendCongSegs = 1
		self.sendMSS = 1000 
		self.seqn = 0
		self.congMode = CONG_SLOWSTART
		self.tsLastChange = 0 
		
		#data, datalock, client):
		self.rttim = RetransmitTimer(self.sendBuff, self.sendLock, self)
		self.rttim.start()
		
	
	def congOnAck(self, segs):
		"""
		this will change the congestion window based on the number of segments that have been Ack'd
		"""
		old = self.sendCongSegs
		if self.congMode == CONG_SLOWSTART:
			self.sendCongSegs += 1
			self.tsLastChange = time.time()
		
		#FIXME
		self.rttim.congMSS = self.sendCongSegs #Fail, Big time
		print "congOnAck Old:", old, "new", self.sendCongSegs
	
	def genSyn(self):
		"""
		If we're making the connection, I say!
		"""
		self.connid = random.randint(0, 2**32-1)
		
	
	def fromSyn(self, nspack, ipport):
		"""
		Just got a syn packet, create a new socket. 
		"""
		self.state = STATE_SYNACK
		self.connid = nspack.connid
		self.dip = ipport[0]
		self.dport = ipport[1]
		
	def ackSyn(self):
		"""
		This will create a SynAck packet to reply
		"""
		nsp = NSPack.NSPack()
		nsp.synf = True
		nsp.ackf = True
		nsp.create()
		
		self.sendsoc(nsp.header, (self.dip, self.dport))
	
	def sendAck(self):
		"""
		Once got a data will reply with ack back, this will generate an ack packet and send
		it
		"""
		nsp = NSPack.NSPack()
		nsp.synf = False
		nsp.ackf = False
		nsp.connid = self.connid
		nsp.ackn = self.ackn
		nsp.create()
		
		self.sendsoc(nsp.header, (self.dip, self.dport))
		
	#def sendSynAck(self):
			
	def ourpack(self, nspack, ipport):
		return self.dip == ipport[0] and nspack.connid == self.connid and self.dport == ipport[1]
	
	def bumpData(self, data, seq):
		"""
		Add data into the receive buffer
		"""
		
		#Work out if we have the space...
		
		bytesused = self.lastBytebuff() - self.ackn 
		
		if(bytesused + len(data) > self.rcvBuffSize):
			return False
		
		#Add data in
		addIntoRecvBuf(data, seq, ts)
		return True
		
	def addIntoRecvBuf(self, data, seq, tstamp):
		"""
		Add data into receive buffer
		"""
		
		#print "nsconn addIntoRecvBuf"
		
		
		#Check if seq is already in there
		present = False
		
		with self.rcvLock:
			for s, d, ts in self.rcvBuff:
				if seq == s:
					present = True
					break
		
			if present:
				#print "Repeated SequenceNumber"
				return False
			else:
				#If next seq, increment ack
				#print "seq == self.ack?", seq, self.ackn
				if seq == self.ackn:
					self.ackn += len(data)
					#print "new ackn", self.ackn
			
			i = 0
			for s, d, ts in self.rcvBuff:
				if s > seq:
					break
				i += 1
			self.rcvBuff.insert(i, (seq, data, tstamp))
		
			#print "Added data in"
		
			#Need to signal?
			#if seq == self.ackn:
				
			#print "Latest Packet, SIGNAL!"
			self.rcvLock.notify()
		
			return True
		
		
		
	def getEndOfRecvBuffer(self):
		"""
		This will look into the receive buffer and fetch data upto the ackn
		"""		
		#print "nsconn endofrecvbuff"
		dreturn = ""
		remove = []
		i = 0
		with self.rcvLock:
			for s, d, ts in self.rcvBuff:
				#print "is ", self.ackn, ">", s+len(d) 
				if self.ackn >= s+len(d):
					remove.append(i)
					dreturn += d
					i+= 1
				else:
					break
			
			if i == 0:
				#print "nsconn endofrecvbuff rtn None"
				return None
			
			self.rcvBuff = self.rcvBuff[i:]
			print "nsconn endofrecvbuff rtn str"
			return dreturn
			
	
	def lastBytebuff(self):
		"""
		Will return the last seq byte in the recv buffer
		"""
		
		if len(self.recvBuff) == 0:
			return self.ackn
		
		s, d = self.recvBuff[-1]
		
		return s + len(d)
		
		
	
	
	
	def recvPack(self, nspack, ts):
		
		if nspack.justSyn():
			#print "RecvPack, Just Syn"
			if self.state == STATE_SYNACK:
				#Reply with a SYNACK again
				#print "State is synack, resending synack"
				self.ackSyn()
			else:
				#print "Just Just Syn with a connection already made..."
				return
		
		
		elif nspack.justSynAck():
			self.state = STATE_CONNECTED
			nsp = NSPack.NSPack()
			nsp.connid = nspack.connid
			nsp.ackf = True
			nsp.create()
			self.sendsoc(nsp.header, nspack.ipport)
		
		elif nspack.hasPayload():
			#print "has payload!"
			self.addIntoRecvBuf(nspack.payload, nspack.seqn, ts)
			#ack has been updated, send ack back!
			self.sendAck()
			
		else:
			#No Syn/Ack flag, read Ack number and update ourself
			#print "Got ackheader only", nspack.ackn
			self.updateToAck(nspack.ackn)
			
			
	
	
	def read(self, to=5):
		"""
		Will wait for data
		"""
		now = time.time()
		with self.rcvLock:
			while True:
				#Check data
				a = self.getEndOfRecvBuffer()
				
				#got something, return it
				if a != None:
					#print "Data not none, rtn"
					return a
				
				
				#otherwise wait for signal
				sleeptime = 5 - (time.time() - now)
				#print "Data is none, sleep on it", sleeptime
				if sleeptime<0:
					#print "nscon read sleep ended"
					return None
				
				self.rcvLock.wait(sleeptime)
	
	def sendWithData(self, data, seq):
		"""
		Will generate a sequence containing the latest conditions of the connection as well as that seq and data
		"""
		#print "details: s:", seq, "connid", self.connid, "ackn", self.ackn, "pls", len(data)
		nsp = NSPack.NSPack()
		nsp.seqn = seq 
		nsp.connid = self.connid
		nsp.ackn = self.ackn
		nsp.payload = data
		nsp.create()
		
		self.sendsoc(nsp.data, self.ipport)
		
		
		
	def sendBuffSize(self):
		"""
		Will return number of bytes in sendbuffer
		"""
		size = 	0
		for s, d, ts in self.sendBuff:
			size += len(d)
	
	def pushOnSendBuff(self, data):
		"""
		Will push data onto sending buffer, May send if no outstanding packets..
		"""
		
		with self.sendLock:
			toSend = False
			if self.sendBuffSize() == 0:
				toSend = True
			#print "buff to send:", toSend
			seq = self.seqn
			#print "seq set as", seq
			
			
			while len(data) != 0:
				a = data[:self.sendMSS]
				data = data[self.sendMSS:]
				self.sendBuff.append((seq, a, None))
				seq += len(a)
				#Signal, And kickstart retransmit timer
			
			self.seq = seq
			self.sendLock.notify()
		
	
	
	def updateToAck(self, n):
		"""
		We got Ack of n, clear send buffer of data up to n,
		May wish to put congestion control here?
		"""
		i = 0
		rm = []
		with self.sendLock:
			for s, d, ts in self.sendBuff:
				#print "updateToAck s < n", s+len(d), n
				if (s+len(d)) <= n:
					i += 1
					rm.append((s,d,ts))
				else:
					break
		
			#print "updateToAck i", i
			for x in rm:
				self.sendBuff.remove(x)
			#print "updatetoAck SB", self.sendBuff
			
			#Congestion Control
			self.congOnAck(i)
			
			self.sendLock.notify()	
	
	def send(self, data, to=1):
		#print "NS con Send!"
		#Calculate size
		with self.sendLock:
			if self.sendBuffSize() >= self.sendMSS*self.sendCongSegs:
				#Pause
				#print "Send buffer full, please hold"
				return False
			else:
				#push it on
				#print "Pushing on data to buffer"
				self.pushOnSendBuff(data)
				return True
	
	def onTimeout(self, n=1):
		"""
		On timeotu
		"""
		print "onTimeout called"
		
	
	def close(self):
		self.rttim.isDead = True
		self.rttim.join()
		
		
		
			
