import struct


class SSPack():

	def __init__(self):
		self.ackNo = -1
		self.segNo = -1
		self.sourceTS = 0
		self.lastDestinationTS = 0
		self.ackList = []
		self.rackList = [] # Reduced Ack list!	
		self.payload = ""
		
		self.data = None
		
		self.compressor = True
	
	def __str__(self):
		"""
		"""
		
		if len(self.payload) > 0:
			s = "Seg: "+str(self.segNo)+" DataL: "+str(len(self.payload))
		else:
			s = "ACK: "+str(self.ackNo) + "Acklist: "+str(self.ackList)
		
		return s
	
	def make(self):
		"""
		Will make data string of packet....
		"""
		
		self.data = struct.pack("lldd", self.ackNo, self.segNo, self.sourceTS, self.lastDestinationTS)
		
		if self.compressor:
			self.ackListToR()
			ackList = self.rackList
		else:
			ackList = self.ackList
		
		self.data += struct.pack("l", len(ackList))	
		for n in ackList:
			self.data += struct.pack("l", n)
		
		self.data += struct.pack("l", len(self.payload))
		
		self.data += self.payload
		
	def ackListToR(self):
		"""
		Will produced reduced Acklist!
		"""
		
		self.rackList = []
		i = 0
		baseSeg = None
		count = 0
		while i < len(self.ackList):
			if baseSeg == None:
				baseSeg = self.ackList[i]
			segn = self.ackList[i]
			#Check if Next segment is 
			if i+1 < len(self.ackList):
				if segn+1 == self.ackList[i+1]:
					count += 1
				
				else:
					self.rackList.append(baseSeg)
					self.rackList.append(count)
					count = 0
					baseSeg = self.ackList[i+1]
			else:
				self.rackList.append(baseSeg)
				self.rackList.append(count)
			
			i += 1
	
	def rackToAckList(self):
		"""
		Will decompress reduced Acklist
		"""
		
		i = 0
		self.ackList = []
		
		while i < len(self.rackList):
			o = self.rackList[i]
			l = self.rackList[i+1]
			self.ackList.append(o)
			for n in xrange(l):
				self.ackList.append(o+n+1)
			i += 2
			#print i, len(self.rackList)
			#print self.rackList
		
			
			
		
	
	def read(self, data):
		self.ackNo, self.segNo, self.sourceTS, self.lastDestinationTS = struct.unpack("lldd", data[0:32])
		acklistlen = struct.unpack("l", data[32:40])[0]
		#self.ackList = []
		ackList = []
		
		print "acklistlen", acklistlen
		for i in range(acklistlen):
			s = i*8 + 40
			ackList.append(struct.unpack( "l", data[s:s+8] )[0] )
			
		if self.compressor:
			self.rackList = ackList
			self.rackToAckList()
		else:
			self.ackList = ackList
			
		payloadi = 40+8*acklistlen
		payloadsize = struct.unpack( "l", data[payloadi:payloadi+8] )
		self.payload = data[payloadi+8:]
		
	def __eq__(self, p):
		if self.ackNo != p.ackNo:
			return False
		if self.segNo != p.segNo:
			return False
		if self.sourceTS != p.sourceTS:
			return False
		if self.lastDestinationTS != p.lastDestinationTS:
			return False
		
		for n in self.ackList:
			if not n in p.ackList:
				return False
		
		if len(self.ackList) != len(p.ackList):
			return False
		
		if self.payload != p.payload:
			return False
		
		return True
