"""
This will be a client that will connect to a server.Listen class
"""

import socket
import threading
import NSPack
import time
import NSConnection

STATE_SYN = 0
STATE_CONNECTED = 1

class NSClient(threading.Thread):
	
	def __init__(self):
		threading.Thread.__init__(self)
		self.port = None
		self.dip = None
		self.sip = None
		
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.setblocking(0)
		self.soc.settimeout(1)
		self.lock = threading.Lock()
		
		self.statecond = threading.Condition()
		self.state = None
		self.isDead = False
		
		self.nsconn = NSConnection.NSConnection()
		
		self.synsent = None
	
	def connect(self, ipport):
		
		self.ipport = ipport
		self.port = ipport[1]
		self.dip = ipport[0]
		
		#Create and send SYN nspack
		nsp = NSPack.NSPack()
		self.nsconn.sendsoc = self.sendToSoc
		nsp.synf = True
		nsp.create()
		
		self.start()
		self.synsent = time.time()
		self.soc.sendto(nsp.header, self.ipport)
		self.changeState(STATE_SYN)
		
		#Wait for synack.... 
		
		result = self.waitForState(STATE_CONNECTED)
		
		#if result:
			#nsconn.state = NSConnection.STATE_CONNECTED
			#nsconn.sendsoc = self.soc.sendto
		if not result:
			#Failed :(
			print "Failed"
			self.close()
		
		return result
		
	def waitForState(self, state, to=3.0):
		"""
		Will lock and block until a state is reached
		"""
		result = False
		self.statecond.acquire()
		if state != self.state:
			self.statecond.wait(to)
		result = (state == self.state)
		self.statecond.release()
		return result
		
	def run(self):
		"""
		Will just listen for data and process them!
		"""
		
		#Wait until we're connected?
		while 1:
			print "waiting for syn"
			if self.isDead:
				
				break
			
			if self.waitForState(STATE_SYN, to=1):
				break
		#ts = time.time()
		#rtt = ts-self.synsent
		
		#print "handshake rtt =", rtt
		#self.nsconn.rttim.rtt = rtt
		#self.nsconn.ackn 
		
		print "syn has sent!"
		#Now we can listen for datas
		while 1:
			if self.isDead:
				break
			try:
				d, ipport = self.soc.recvfrom(2048)
				print "Got Packet!"
			except socket.timeout:
				continue
			tr = time.time()
			nsp = NSPack.NSPack(d)
			nsp.ipport = ipport
			
			if not nsp.valid:
				print "Invalid packet. IMPOSSIBU!"
				continue
			
			print "Sending it to recvPack"
			self.nsconn.recvPack(nsp, tr)
			
			if self.nsconn.state == NSConnection.STATE_CONNECTED:
				
				rtt = tr-self.synsent
				print "handshake rtt =", rtt
				self.nsconn.rttim.rtt = rtt
				self.nsconn.ackn = nsp.seqn
				self.nsconn.connid = nsp.connid
				self.nsconn.ipport = ipport
				self.changeState(STATE_CONNECTED)
			
				
			
			
	def sendToSoc(self, data, ipport):
		print "sendToSoc!"
		self.soc.sendto(data, ipport)
		
	def changeState(self, state):
		self.statecond.acquire()
		self.state = state
		self.statecond.notify()
		self.statecond.release()
		
	def send(self, data):
		#time.sleep(1)
		self.nsconn.send(data)
	
	def close(self):
	
	
		self.isDead = True
		
		self.nsconn.close()
		self.join()
		self.soc.close()
		
