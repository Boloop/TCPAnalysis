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

def setCongControl(p):
	def _setFile(s, args):
		i = None
		if len(args)>1:
			i = args[1]
			
		
		if i != None:
			p.congControl = i
		
		s.soc.send("CCNT: "+p.congControl+";\r\n")
	
	return _setFile



class tcpTest(runSoft.runSoft):
	"""
	"""
	
	def __init__(self):
		runSoft.runSoft.__init__(self)
		
		self.congControl = "reno"
		self.ip = "10.0.2.2"
		self.port = "4050"
		self.basePath = "python"
		self.scriptName = "client.py"
		
	def formCommand(self):
		self.command = [self.basePath, self.scriptName, "-Z", self.congControl, self.ip, self.port]
		

if __name__ == "__main__":


	if len(sys.argv) < 5:
		print "please Speicify ip, port, pythonCall, pythonpath"
		sys.exit(-1)
	
	ip = sys.argv[1]
	port = sys.argv[2]
	basePath = sys.argv[3]
	scriptName = sys.argv[4]
	
	print "Running"
	
	sr = tcpTest()
	sr.ip = ip
	sr.port = port
	sr.basePath = basePath
	sr.scriptName = scriptName
	
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
	
	sl.commands.append("CCNT")
	sl.commandactions.append(setCongControl(sr))	
	
	
	if sl.soc == None:
		print "Failed to Listen"
		sys.exit(-1)
	
	sl.start()
	
	a = raw_input("Hit Enter to Quit")
	
	sl.kill()
	if sr.isRunning():
		sr.kill()
	
	
