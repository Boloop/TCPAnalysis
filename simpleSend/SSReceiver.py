
class SSReceiver():

	def __init__(self):
		self.rSegs = []
	
	def onSegment(self, segment):
		if not segment in self.rSegs:
			self.rSegs.append(segment)
