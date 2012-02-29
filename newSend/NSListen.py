# This class will listen for new connections and pass packets onto objects that 
# are already initiated
#


import socket
import threading
import NSPack
import NSConnection
import time


class NSListen(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.lock = threading.Lock()
		self.sendlock = threading.Lock()
		self.connslock = threading.Condition()
		self.isDead = False
		
		self.conns = []
	
	def bind(self, portip):
		self.soc.bind(portip)
		self.soc.setblocking(0)
		self.soc.settimeout(1)
		
	def accept(self, to=1):
		result = None
		i= 0
		self.connslock.acquire()
		for c, a in self.conns:
			if a == False:
				result = c
				break
			i += 1
		if result:
			self.conns[i] = (c, True)
			self.connslock.release()
			return result
		 
		 
		 
		#Else no there wait
		self.connslock.wait(to)
		i = 0
		for c, a in self.conns:
			if a == False:
				result = c
				self.conns[i] = (c, True)
				break
			i += 1
			
				
		self.connslock.release()
		return result
	
	def send(self, d, ipport):
		"""
		Will send data d to ipport
		"""
		
		with self.sendlock:
			try:
				return self.soc.sendto(d, ipport)
			except:
				return False
	
	def run(self):
	
		while 1:
			if self.isDead:
				break

			try:
				d, ipport = self.soc.recvfrom(2048)
				
			except socket.timeout:
				continue
				
			tr = time.time()
			print "got packet!"
			nspack = NSPack.NSPack(d)
			if not nspack.valid:
				print "Unable to read"
				continue
			
			#Is that a connection already here?
			found = None
			with self.connslock:
				
				for c, a in self.conns:
					print "Ittering", c, a
					if c.ourpack(nspack, ipport):
						found = c
						break
			if found:
				#Give to connection
				found.recvPack(nspack, tr)
			elif nspack.justSyn():
				#create a new one? o.o
				print "Got a syn, adding into list!"
				nsconn = NSConnection.NSConnection()
				nsconn.fromSyn(nspack, ipport)
				nsconn.sendsoc = self.send
				
				#Send synack!
				nsconn.ackSyn()
				nsconn.ackn = nspack.seqn
				
				self.connslock.acquire()
				self.conns.append((nsconn, False))
				self.connslock.notify()
				self.connslock.release()
				
				
			else:
				print "Got invalid packet"
		
		self.soc.close()	
				
					
