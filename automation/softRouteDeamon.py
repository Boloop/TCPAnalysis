"""
Will listen to a socket...
"""

import socLis
import runSoft
import sys

def isRunning(p):
	def _isRunning(s, args):
		a = p.isRunning()
		s.soc.send("IR: "+str(a)+";\r\n")
	return _isRunning

def execute(p):
	def _execute(s, args):
		p.runCommand()
		s.soc.send("EX: "+str(p.callSuccess)+";\r\n")
	
	return _execute
	
def kill(p):
	def _kill(s, args):
		p.kill()
		s.soc.send("KL: ;\r\n")
	
	return _kill

def dataRate(p):
	def _dataRate(s, args):
		i = None
		if len(args)>1:
			si = args[1]
			try:
				i = int(si)
			except:
				pass
		
		if i != None:
			p.dataRate = i
		
		s.soc.send("DATAR: "+str(p.dataRate)+";\r\n")
	
	return _dataRate
	
def forwardDrop(p):
	def _forwardDrop(s, args):
		i = None
		if len(args)>1:
			si = args[1]
			try:
				i = int(si)
			except:
				pass
		
		if i != None:
			p.forwarddr = i
		
		s.soc.send("FORDR: "+str(p.forwarddr)+";\r\n")
	
	return _forwardDrop

def retryLimit(p):
	def _retryLimit(s, args):
		i = None
		if len(args)>1:
			si = args[1]
			try:
				i = int(si)
			except:
				pass
		
		if i != None:
			p.retryLimit = i
		
		s.soc.send("RETL: "+str(p.retryLimit)+";\r\n")
	
	return _retryLimit


class softRoute(runSoft.runSoft):
	"""
	"""
	
	def __init__(self):
		runSoft.runSoft.__init__(self)
		
		self.forwarddr = 1
		self.backwarddr = 1
		self.dataRate = 100000
		self.arpPath = ""
		self.int1 = "eth1"
		self.int2 = "eth2"
		self.basePath = "./softRoute"
		self.retryLimit = 1
		
	def formCommand(self):
		self.command = [self.basePath, "-or", str(self.dataRate),
			"-dr", str(self.forwarddr), "-drb", str(self.backwarddr),
			"-a", self.arpPath, "-rl", str(self.retryLimit), self.int1, self.int2]
		

if __name__ == "__main__":


	if len(sys.argv) < 3:
		print "Please enter path for softRoute and arptable"
		sys.exit(-1)
	
	path = sys.argv[1]
	arptable = sys.argv[2]
	print "Running"
	
	sr = softRoute()
	sr.basePath = path
	sr.arpPath = arptable
	
	sr.runCommand()
	if not sr.callSuccess:
		print "Problem calling command"
		sys.exit(-1)
	sr.kill()
	
	sl = socLis.Listen()
	
	sl.commands.append("IR")
	sl.commandactions.append(isRunning(sr))
	
	sl.commands.append("EX")
	sl.commandactions.append(execute(sr))
	
	sl.commands.append("KL")
	sl.commandactions.append(kill(sr))
	
	sl.commands.append("DATAR")
	sl.commandactions.append(dataRate(sr))	
	
	sl.commands.append("FORDR")
	sl.commandactions.append(forwardDrop(sr))
	
	sl.commands.append("RETL")
	sl.commandactions.append(retryLimit(sr))
	
	if sl.soc == None:
		print "Failed to Listen"
		sys.exit(-1)
	
	sl.start()
	
	a = raw_input("Hit Enter to Quit")
	
	sl.kill()
	if sr.isRunning():	
		sr.kill()
	
	
