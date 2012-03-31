
class SSPack():

	def __init__(self):
		self.ackNo = 0
		self.SourceTS = 0
		self.lastDestinationTS = 0
		self.ackList = []	
		self.payload = ""
