"""
This will hold modules to run CLI programs in the background, provide mangement to them.
Basically a wrapper for popen
"""

import subprocess
import os


def amIRoot():
	"""
	Return bool if we are root
	"""
	return os.getuid() == 0
	
class runSoft(object):
	def __init__(self):
		self.p = None
		self.command = ["ping", "127.0.0.1"]
		self.callSuccess = False
	def isRunning(self):
		"""
		Will return bool if presently running
		"""
		if self.p == None:
			return False
			
		try:
			a = self.p.poll()
		except:
			return False
		
		if a == None:
			return True
		else:
			return False
	
	
	def formCommand(self):
		self.command = ["ping", "127.0.0.1"]
	
	def runCommand(self):
		"""
		Will run the command
		"""
		
		self.formCommand()
		try:
			self.p = subprocess.Popen(self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			self.callSuccess = True
		except OSError:
			self.callSuccess = False
			print "Failed to Call command"
	
	
	def comms(self, data=None):
		"""
		Wil communicate data to the application
		(good to kill them off)
		"""
		if self.p == None:
			return
		
		self.p.communicate(input=data)
	
	def kill(self):
		"""
		Calls the kill command
		"""
		
		if self.p == None:
			return
		if self.isRunning():
			self.p.kill()
