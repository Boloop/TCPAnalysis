
class SSPack():

	def __init__(self):
		self.ackNo = -1
		self.segNo = -1
		self.sourceTS = 0
		self.lastDestinationTS = 0
		self.ackList = []	
		self.payload = ""
	
	def __str__(self):
		"""
		"""
		
		if len(self.payload) > 0:
			s = "Seg: "+str(self.segNo)+" DataL: "+str(len(self.payload))
		else:
			s = "ACK: "+str(self.ackNo)
		
		return s
		 
