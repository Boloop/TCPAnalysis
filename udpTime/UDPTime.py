import time
import struct
import datetime
import threading
import socket


class UDPTimePacket(object):
	def __init__(self, data=None):
		
		self.t1      = None
		self.t2      = None
		self.t3      = None
		self.t4      = None
		
		self.stage   = None
		self.seq     = None
		self.padding = None
		
		self.bin = data
		self.valid = None
		
		if data != None:
			#Read Bin!
			self.valid = self.readBin(data)
	
	def readBin(self, data):
		
		if len(data) < 40:
			return False
		
		self.seq, self.stage = struct.unpack(">II", data[0:8])
		
		if self.stage >= 1:
			#Just decode the first
			t1a, t1b = struct.unpack(">II", data[8:16])
			self.t1 = datetime.datetime.fromtimestamp(t1a+t1b/1000000.)
		if self.stage >= 2:
			#Just decode the first
			t2a, t2b = struct.unpack(">II", data[16:24])
			self.t2 = datetime.datetime.fromtimestamp(t2a+t2b/1000000.)
		if self.stage >= 3:
			#Just decode the first
			t3a, t3b = struct.unpack(">II", data[24:32])
			self.t3 = datetime.datetime.fromtimestamp(t3a+t3b/1000000.)
		if self.stage >= 4:
			#Just decode the first
			t4a, t4b = struct.unpack(">II", data[32:40])
			self.t4 = datetime.datetime.fromtimestamp(t4a+t4b/1000000.)
		
		self.padding = len(data)-40
		
		return True
	
	def create(self):
		
		if not self.seq or not self.stage:
			return False
		
		d = struct.pack(">II", self.seq, self.stage)
		
		t1a = 0
		t1b = 0
		t2a = 0
		t2b = 0
		t3a = 0
		t3b = 0
		t4a = 0
		t4b = 0
		
		
		if self.t1:
			t1a = int(time.mktime(self.t1.utctimetuple()))
			t1b = self.t1.microsecond
		if self.t2:
			t2a = int(time.mktime(self.t2.utctimetuple()))
			t2b = self.t2.microsecond
		if self.t3:
			t3a = int(time.mktime(self.t3.utctimetuple()))
			t3b = self.t3.microsecond
		if self.t4:
			t4a = int(time.mktime(self.t4.utctimetuple()))
			t4b = self.t4.microsecond
		
		
		d += struct.pack(">IIIIIIII", t1a, t1b, t2a, t2b, t3a, t3b, t4a, t4b)
		
		if self.padding:
			d += "X"*self.padding
		
		self.bin = d
		
		return True
	

class Server(threading.Thread):
	"""
	This is a server that will be a thread
	"""
	
	def __init__(self, port):
		threading.Thread.__init__(self)
		
		self.port = port
		
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.soc.setblocking(False)
		self.soc.settimeout(1)
		self.dead = False
		
		self.lock = threading.Lock()
		
	def bind(self):
		print "Binding to port:", str(self.port)
		self.soc.bind(("", self.port))
	
	def run(self):
		
		while 1:
			with self.lock:
				if self.dead:
					break
					
			try:
				data, add = self.soc.recvfrom(2048)
			
			except socket.timeout:
				continue
				
			
			tpkt = UDPTimePacket(data)
			
			if not tpkt.valid:
				continue
			
			if tpkt.stage == 1:
				#Place in t2 for us
				tpkt.t2 = datetime.datetime.now()
				tpkt.stage += 1
				
			elif tpkt.stage == 3:
				#Place in t4 for us
				tpkt.t4 = datetime.datetime.now()
				tpkt.stage += 1
			
			else:
				continue
			
			#Send packet back!
			tpkt.create()
			
			self.soc.sendto(tpkt.bin, add)
		
	def die(self):
		with self.lock:
			self.dead = True 
			
			
			
			
class Client(threading.Thread):

	def __init__(self, ip, port, seq, padding):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		self.seq = seq
		self.padding = padding
		
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		self.soc.setblocking(False)
		self.soc.settimeout(1)
		self.soc.connect((self.ip, self.port))
		self.dead = False
		self.lock = threading.Lock()
		
		self.timeout = 30
		
		self.timer = 0
		
		self.stage = 0
		
		self.killed = False
		self.timedout = False
		self.invalid = False
		self.txerror = False
		self.dpkt = None
	
	def run(self):
	
		self.stage = 1
		
		self.dpkt = UDPTimePacket()
		self.dpkt.seq = self.seq
		self.dpkt.stage = self.stage
		self.dpkt.t1 = datetime.datetime.now()
		
		self.dpkt.create()
		
		self.soc.send(self.dpkt.bin)
		
		
		self.timer = self.timeout
		while 1:
			
			with self.lock:
				if self.dead:
					self.killed = True
					break
			
			try:
				data = self.soc.recv(2048)
			except socket.timeout:
				self.timer -= 1
				if self.timer < 0:
					self.timedout = True
					break 
				continue
			
			except socket.error:
				#We couldn't send?
				self.txerror = True
				break
			
			self.dpkt = UDPTimePacket(data)
			
			if not self.dpkt.valid:
				self.invalid = True
				break
			print "stageRx", self.dpkt.stage
			if self.stage == 1:
				#Stage two back! Move to 3
				self.stage = 3
				self.dpkt.stage = 3
				self.dpkt.t3 = datetime.datetime.now()
				self.dpkt.create()
				
				self.soc.send(self.dpkt.bin)
			
			elif self.stage == 3:
				#stage 4 received!
				
				
				self.stage = 4
			
				break
		
			
			
		
			
		
