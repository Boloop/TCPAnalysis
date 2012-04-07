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
		self.data += struct.pack("l", len(self.ackList))
		for n in self.ackList:
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
				if segn+1 = self.ackList[i+1]:
					count += 1
				
				else:
					self.rackList.append(baseSeg)
					self.rackList.append(count)
					count = 0:
					baseSeg = self.ackList[i+1]
			else:
				self.rackList.append(baseSeg)
				self.rackList.append(count)
			
			i += 1
		
			
			
		
	
	def read(self, data):
		self.ackNo, self.segNo, self.sourceTS, self.lastDestinationTS = struct.unpack("lldd", data[0:32])
		acklistlen = struct.unpack("l", data[32:40])[0]
		self.ackList = []
		
		for i in range(acklistlen):
			s = i*8 + 40
			self.ackList.append(struct.unpack( "l", data[s:s+8] )[0] )
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
