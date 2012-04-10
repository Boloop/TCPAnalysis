"""
This is the client to SocLis and will send acorss commands and pick up their awnsers
"""

import socket
import threading
import time

class socCmdLisThread(threading.Thread):
	def __init__(self, soc, parent):
		threading.Thread.__init__(self)
		self.dead = False
		self.soc = soc
		self.data = ""
		self.parent = parent
		
		self.d = ""
	
	def run(self):
		while True:
			if self.dead:
				break
			
			try:
				self.d += self.soc.recv(1024)
				print "Got data:", self.d
				self.checkData()
			except socket.timeout:
				pass
		
	
	def checkData(self):
		"""
		This wll check out the data stream
		"""
		while self.d.count(";") != 0:
			c = self.d.split(";")
			
			proc = c[0]
			self.d == ""
			for n in c[1:-1]:
				self.d += n +";"
			self.d += c[-1]
			
			#Proccess the data back
			args = proc.split(" ")
			print "GOT reply", str(args)
		
		pass

class socCmd(object):
	def __init__(self):
		"""
		
		"""
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		self.nIP = "127.0.0.1"
		self.nPort = 5010
		self.lThread = None
		
	def connect(self):
		try:
			self.soc.connect((self.nIP, self.nPort))
			self.soc.setblocking(0)
			self.soc.settimeout(1)
			return True
		except:
			return False
	
	def launchListener(self):
		self.lThread = socCmdLisThread(self.soc, self)
		self.lThread.start()
		
	def close(self):
		if self.lThread != None:
			self.lThread.dead = True
			self.lThread.join()
	
		self.doCommand(["QQQ"])
		time.sleep(1)
	
		
			
		if self.soc != None:
			self.soc.close()
	
	def doCommand(self, command):
		"""
		Will send the command across the pipes
		command is a list of arguments
		"""
		
		d = ""
		for n in command:
			d += str(n) + " "
		d += ";\r\n"
		
		self.soc.send(d)
		
	
	def callIsRunning(self):
		"""
		Will do the command IR
		"""
		
		self.doCommand(["IR"])
		
