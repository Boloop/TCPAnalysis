import socCmd
import time

class tcpDumpClient(socCmd.socCmd):
	def __init__(self):
		socCmd.socCmd.__init__(self)
	
	def changeFileName(self, name):
		now = time.time()
		self.doCommand(["FILE", name])
		self.lThread.waitFor("FILE", now=now)

class softRouteClient(socCmd.socCmd):
	def __init__(self):
		socCmd.socCmd.__init__(self)
	
	def changeDropRate(self, rate):
		now = time.time()
		self.doCommand(["FORDR", str(rate)])
		self.lThread.waitFor("FORDR", now=now)
	
	def changeDataRate(self, rate):
		now = time.time()
		self.doCommand(["DATAR", str(rate)])
		self.lThread.waitFor("DATAR", now=now)

class socketTXClient(socCmd.socCmd):
	def __init__(self):
		socCmd.socCmd.__init__(self)
		
	def changeCongestion(self, cong):
		now = time.time()
		self.doCommand(["CCNT", cong])
		self.lThread.waitFor("CCNT", now=now)

