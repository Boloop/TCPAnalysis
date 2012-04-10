"""
This module will create a network socket that will listen
to connections and perform commands/listen to the protocol
"""

import socket
import threading
import time

class Listen(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
		self.nPort = 9014
		self.nIP = ""
		
		self.dead = False
		self.lock = threading.Lock()
		self.clients = []
		
		self.commands = []
		self.commandactions = []
		
		try:
			self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.soc.bind((self.nIP, self.nPort))
		except:
			self.soc = None
		if self.soc != None:
			self.soc.setblocking(0)
			self.soc.settimeout(1)
		
			self.soc.listen(10)
		
	def removeClient(self, c):
		if c in self.clients:
			self.clients.remove(c)
		
	def run(self):
		pass
		
		while True:
			if self.dead:
				break
			
			try:
				last = time.time()
				a, b = self.soc.accept()
				#Got a
				at = Client(a, self, b)
				with self.lock:
					if self.dead:
						at.close()
						break
					
					self.clients.append(at)
					at.start()
			except socket.timeout:
				if time.time() - last < 0.1:
					break
				pass
		
	def kill(self):
		self.dead = True
		with self.lock:
			lcp = self.clients[:]
			for c in self.clients:
				c.kill()
			
		for c in lcp:
			c.join()
		
		self.join()
		self.soc.close()		
			
			
	
	


class Client(threading.Thread):
	def __init__(self, soc, parent, ipport):
		threading.Thread.__init__(self)
		self.soc = soc
		self.parent = parent
		self.lock = threading.Lock()
		self.dead = False
		self.ipport = ipport
		
		self.backData = ""
		
		self.soc.setblocking(0)
		self.soc.settimeout(1)
	
	def run(self):
		while True:
			if self.dead:
				break
			
			try:
				d = self.soc.recv(1024)
				self.backData += d
				
				#Does data have a command?
				if self.backData.count(";") > 0:
					coms = self.backData.split(";")
					self.backData = coms[-1]
					coms = coms[:-1]
					
					for c in coms:
						#do each command!
						#self.soc.send("C: "+c+"\r\n")
						c = c.strip()
						self.doCommand(c.split(" "))
						
			except socket.timeout:
				pass
			
			except:
				self.parent.removeClient(self)
				try:
					self.kill()
				except:
					pass
				print "Killing Self :(", self.ipport
				break
	
	def doCommand(self, args):
		"""
		"""
		c = args[0]
		if c == "lsc":
			a = self.parent.clients[:]
			i = 1
			result = "lsc: \r\n"
			for b in a:
				result += str(i)+": "+str(b.ipport)+"\r\n"
			result += ";"
			self.soc.send(result)
		elif c == "QQQ":
			self.soc.send("QQQ: QUITING;\r\n")
			self.kill()
			
		elif c in self.parent.commands:
			#Get index
			i = 0
			while self.parent.commands[i] != c:
				i += 1
			
			self.parent.commandactions[i](self, args)
		
		else:
			self.soc.send("Unknown Command: "+c+"\r\n")
			
				
	
	def kill(self):
		self.dead = True
		self.soc.close()
		
		
	
