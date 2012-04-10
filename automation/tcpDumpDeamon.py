"""
Will listen to a socket...
"""

import socLis
import runSoft
import sys
import time
import subprocess

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
		#p.kill()
		#p.comms()
		if p.isRunning():
			p.p.send_signal(subprocess.signal.SIGINT)
			#p.p.send_signal(subproces.signal.SIGINT)
		s.soc.send("KL: ;\r\n")
	
	return _kill

def setFile(p):
	def _setFile(s, args):
		i = None
		if len(args)>1:
			i = args[1]
			
		
		if i != None:
			p.dataPath = i
		
		s.soc.send("FILE: "+p.dataPath+";\r\n")
	
	return _setFile



class tcpDump(runSoft.runSoft):
	"""
	"""
	
	def __init__(self):
		runSoft.runSoft.__init__(self)
		
		self.dataPath = "Default"
		self.int1 = "eth1"
		self.basePath = "tcpdump"
		
	def formCommand(self):
		self.command = [self.basePath, "-i", self.int1, "-w", self.dataPath]
		

if __name__ == "__main__":


	if len(sys.argv) < 2:
		print "please Speicify Interface"
		sys.exit(-1)
	
	interface = sys.argv[1]
	
	print "Running"
	
	sr = tcpDump()
	sr.int1 = interface
	
	sr.runCommand()
	if not sr.callSuccess:
		print "Problem calling command"
		sys.exit(-1)
	time.sleep(5)
	sr.kill()
	
	sl = socLis.Listen()
	
	sl.commands.append("IR")
	sl.commandactions.append(isRunning(sr))
	
	sl.commands.append("EX")
	sl.commandactions.append(execute(sr))
	
	sl.commands.append("KL")
	sl.commandactions.append(kill(sr))
	
	sl.commands.append("FILE")
	sl.commandactions.append(setFile(sr))	
	
	
	if sl.soc == None:
		print "Failed to Listen"
		sys.exit(-1)
	
	sl.start()
	
	a = raw_input("Hit Enter to Quit")
	
	sl.kill()
	if sr.isRunning():	
		sr.kill()
	
	
