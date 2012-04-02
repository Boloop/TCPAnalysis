import socket
import threading
import time

def packetCall(pkt):
	print "got pkt len", len(pkt)


class listen(threading.Thread):
	"""
	This class listens, and plays on the first packet
	"""
	def __init__(self, nPort):
		threading.Thread.__init__(self)
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		self.dead = False
		self.binded = False
		self.onPacket = packetCall
		self.firstSend = None
		
		try:
			self.soc.bind(("", nPort))
			self.binded = True
		except:
			return
		
		self.soc.setblocking(0)
		self.soc.settimeout(1)
		
		#self.start()
	
	
	def send(self, p):
		"""
		Will send P packet
		"""
		if self.firstSend == None:
			return # Need first packet in FIRST!
		if self.dead:
			return
		self.soc.sendto(p, self.firstSend)
		
			
			
	def run(self):
		while True:
			if self.dead:
				break
				
			
			try:
				d, add = self.soc.recvfrom(2048)
				#print d, add
				#d = self.soc.recvfrom(2048)
				#add = 1
				
			except socket.timeout:
				continue
			
			if self.firstSend == None:
				print "First Blood"
				self.firstSend = add
			elif self.firstSend != add:
				print "Wrong Source"
				continue
			
			self.onPacket(d)
				
	def close(self):
		self.dead = True
		if self.isAlive(): 
			self.join()
		self.soc.close()
		
			
				
			
class sender(threading.Thread):
	def __init__(self, ip, nPort):
		threading.Thread.__init__(self)
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.setblocking(0)
		self.soc.settimeout(1)
		
		self.dead = False
		self.sentPacketYet = False
		self.onPacket = packetCall
		
		self.ip = ip
		self.nPort = nPort
		
	def send(self, p):
		"""
		Will send P packet
		"""
		
		
		if self.dead:
			return
			
		self.soc.sendto(p, (self.ip, self.nPort))
		self.sentPacketYet = True
	
	def run(self):
		while True:
			if self.dead:
				return
			
			if not self.sentPacketYet:
				#print "Snoor"
				time.sleep(0.1)
				continue
			
			#listen
			
			try:
				d = self.soc.recv(2048)
								
			except socket.timeout:
				#print "TO udp"
				continue
			
			self.onPacket(d)
	
	def close(self):
		self.dead = True
		if self.isAlive(): 
			self.join()
		self.soc.close()
	
