"""
SpeedPacket is a class that will read and construct a udp packet structure
The packet will have information such as it's Sequence, When the last packet is,
what the TX rate is etc...
"""

import struct
import threading
import socket
import time
import random

class SpeedPacket(object):

	def __init__(self, data=None):
		self.data = data
		self.seq = 0
		self.lastSeq = 0
		self.size = 0
		self.txRate = 0
		self.id = 0
		
		self.validPacket = False # This is an error flag used when reading/writing packes
					 # Tells us if there is an error or not 
		
		if data != None: 
			self.readFromData(self.data)
		
	
	def readFromData(self, data):
		"""
		This will read in a packet and read in the variables and set them up
		as the member variables of this class
		"""
		self.data = data
		try:
			self.id, self.seq, self.lastSeq, self.txRate = struct.unpack("LLLL", self.data[0:32])
		except:
			self.validPacket = False
			return self.validPacket
		
		self.size = len(self.data)
		
		self.validPacket = True
		return self.validPacket
	
	def __str__(self):
		"""
		"""
		
		return "spdPkt ID: "+str(self.id)+" Last Seq:"+str(self.lastSeq)+" seq:"+str(self.seq)+" txRate: "+str(self.txRate)
	
	def create(self):
		"""
		Will return data that will be a constructed data packet
		"""
		self.data = ""
		self.data += struct.pack("LLLL", self.id, self.seq, self.lastSeq, self.txRate)
	
		rData = self.size-len(self.data) # Work out how much padding we need to make the packet fit to size
		
		if rData > 0:
			self.data += "X"*rData
		elif rData < 0:
			self.validPacket = False
			return None
			
		return self.data



class SpeedConnection(object):
	"""
	This clas will hold all the details for a particular ID
	"""
	
	def __init__(self, spdPkt):
		"""
		Initialise with the speedPacket
		"""
		
		self.id = spdPkt.id
		self.txRate = spdPkt.txRate
		self.lastSeq = spdPkt.lastSeq
		self.size = spdPkt.size
		
		self.seqs = [spdPkt.seq]
		self.count = 1
		
		self.totalSize = spdPkt.size
		
		self.firstTS = time.time()
		self.lastTS = time.time()
		self.lastSeq = 0

	def doesIDMatch(self, spdPkt):
	
		return self.id == spdPkt.id
	
	def addPacket(self, spdPkt):
		self.count += 1
		self.totalSize += spdPkt.size
		self.seqs.append(spdPkt.seq)
		self.lastTS = time.time()
		#self.lastSeq = spdPkt.seq
		
	def __str__(self):
	
		speed = "UNKOWN"
		if self.lastTS != self.firstTS:
			speed = self.totalSize/(self.lastTS - self.firstTS)
			
		return "ID: "+str(self.id)+" Last Seq:"+str(self.lastSeq)+" LRcvdSeq:"+str(self.seqs[-1])+" Speed: "+str(speed)



class SpeedSend(threading.Thread):
	"""
	This is a class that wil be sending UDP packets at a set rate and size 
	"""
	
	def __init__(self,  port=12121, host="localhost"):
	 	
		threading.Thread.__init__(self)
		self.port = port
		self.host = host
		
		self.running = False
		self.isDead = False
	 	
		self.soc  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.connect((host, port))
	
		self.datasize = 1400
		self.datarate = 128000000
		self.id = random.randint(0,2**32-1)
		
		self.timeout = 20
	
	def setPacketSize(self, size):
		"""
		This will set the size of each packet
		"""
		
		self.datasize = size
	
	def setDataRate(self, rate):
		"""
		This will set the TXrate in bytes/sec
		"""
		
		self.datarate = rate
		
	def fire(self):
		"""
		This will run through the whole program
		"""
		
		packetrate = float(self.datarate)/self.datasize
		packetperiod = 1/packetrate

		
		seq = -1
		spdPkt = SpeedPacket()
		spdPkt.id = self.id
		spdPkt.seq = seq
		spdPkt.txRate = self.datarate
		spdPkt.lastSeq = int(self.timeout/packetperiod)
		spdPkt.size = self.datasize
		
		print "ID:"+str(spdPkt.id)+" lastSeq:"+str(spdPkt.lastSeq)+" Rate:"+str(self.datarate)

		starttime = time.time()
		timenow = time.time()
		while timenow-starttime < self.timeout:
			
			spdPkt.seq += 1
			#print "send", str(spdPkt)
			
			self.soc.send( spdPkt.create() )
			
						
			timenownow = time.time()
			sleeptime = packetperiod*(spdPkt.seq+1) - (timenownow-starttime)
			#sleeptime = packetperiod-timenownow+timenow
			
			if sleeptime > 0:
				#print "Sleep", sleeptime
				time.sleep(sleeptime)
			timenow = timenownow
			
			
			
			if spdPkt.seq  == spdPkt.lastSeq:
				break
		print "FIN?"
			
	def setTimeout(self, to):
		"""
		This will set how long the connection will last at most
		"""
		self.timeout = to
		
		
	
	

		
class SpeedListen(threading.Thread):
	"""
	This class will contain a whole service of listening and sorting out packet streams
	"""
	def __init__(self, port=12121):
		
		threading.Thread.__init__(self)
		self.port = port

		self.conns = [] # list of connections
		
		self.running = False
		self.isDead = False
		self.binded = False

		self.soc  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.setblocking(False)
		self.soc.settimeout(0.5)
		try:
			self.soc.bind(("", port))
			self.binded = True
		except:
			print "Unable to bind to the fudge"
			
	def run(self):

		while True:
			try:
				data, addr = self.soc.recvfrom(2048)
			except socket.timeout:
				#Timed out, check if we're dead?
				if self.isDead:
					break
				continue
			
			#Process the Data?
			spdPkt = SpeedPacket(data)
			if not spdPkt.validPacket:
				print "Received broken packet"
				continue
			
			#print "Got: "+str(spdPkt)
			
			isNew = True
			for spdCon in self.conns:
				if spdCon.doesIDMatch(spdPkt):
				
					isNew = False
					spdCon.addPacket(spdPkt)
					break
			
			if isNew:
				self.conns.append(SpeedConnection(spdPkt))
				print "Got a new ID of:", spdPkt.id

		
		print "Shutting down :("
	
	
	def printSummary(self):
		print "There is", len(self.conns), "Connections"
		for spdCon in self.conns:
			print str(spdCon)
	
	def reset(self):
		print "Reset Stats"
		self.conns = []
	
	def stop(self):
		"""
		This will flag the system it's dead and to stop :(
		"""
		self.isDead = True
