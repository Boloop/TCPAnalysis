import SSPack


class SSReceiver():

	def __init__(self):
		self.ackNo = -1
		self.rSegs = []
		self.sendCall = None
		self.lsTime = -1
		
	def __str__(self):
		s = "ackNo: "+str(self.ackNo)+" rSegs: "+str(self.getSegNumbers())+" lst: "+str(self.lsTime)
		return s
	
	def getSegNumbers(self):
		result = []
		for p in self.rSegs:
			result.append(p.segNo)
		return result 
	
	def onSegment(self, segment):
		#Update Time
		if segment.sourceTS > self.lsTime:
			self.lsTime = segment.sourceTS
		
		#Add the Data?
		if segment.segNo <= self.ackNo:
			pass # We've already counted this
		else:
			found = False
			for p in self.rSegs:
				if p.segNo == segment.segNo:
					found = True
					break
			
			if not found:
				self.rSegs.append(segment)
		#elif not segment in self.rSegs:
		#	self.rSegs.append(segment)
		
		#Flush + Work out the ackNo
		if self.ackNo < 0:
			self.ackNo = segment.segNo-1
				
				
		self.recalcAck()
		print "recal ACK "+str(self.ackNo)
		d = self.flushData()
		
		
		
		
		#Construct Ack Data
		ack = SSPack.SSPack()
		ack.ackNo = self.ackNo
		ack.ackList = self.genAckList()
		
	def sendPacket(self, pack):
		"""
		This is a PRIVATE method, called internally to send the call send method
		"""
		
		self.sendCall(pack)
	
	def genAckList(self):
		"""
		Returns a list of Segs to SACK.
		"""
		result = []
		for p in self.rSegs:
			result.append(p.segNo)
		return result
	
	def flushData(self):
		"""
		Will return sequence of packets to flush out the data
		Get the smallest, and go in order upto and including ackNo
		"""
		
		#Find smallest Segment
		smallest = None
		for p in self.rSegs:
			if smallest == None:
				smallest = p.segNo
			elif smallest > p.segNo:
				smallest = p.segNo
		
		if smallest > self.ackNo:
			return ""
		
		if self.ackNo < 0:
			return ""
		
		result = ""
		find = smallest
		rml = []
		first = True
		
		while True:
			found = None
			for p in self.rSegs:
				if p.segNo == find:
					found = p
					break
			
			
			if found != None:
				rml.append(found)
				find += 1
				result += found.payload
			else:
				break
			
		
		for p in rml:
			self.rSegs.remove(p)
		
		
		return result
		
	def recalcAck(self):
		"""
		Will generate lastAckNo and spit it out
		ackNo presently previous round, got new segment, might be it + 1
		"""
		
		#if self.ackNo < 0:
		#	self.ackNo = self.rSegs[0].segNo
		
		
		while True:
			#Find Target segment
			target = self.ackNo + 1
			found = False
			for p in self.rSegs:
				if target == p.segNo:
					self.ackNo += 1
					found = True
					break
			
			#
			if not found:
				break
		
			
