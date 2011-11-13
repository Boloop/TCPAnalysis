"""
This will hold classes for transfering data across a TCP connection
"""

import threading
import socket
import time

class Server(threading.Thread):

	class ClientHandler(threading.Thread):
		def __init__(self, soc, addy):
			threading.Thread.__init__(self)
			self.soc = soc
			self.soc.setblocking(0)
			self.soc.settimeout(1)
			self.addy = addy
			self.lock = threading.Lock()
			self.dead = False
		
		def run(self):
			self.soc.send("Boo")
			while True:
				with self.lock:
					if self.dead:
						break
				
				try:
					data = self.soc.recv(2048)
					
					#Does it end in FIN?
					if data[-3:] == "FIN":
						#Shutdown
						self.soc.send("\r\n\r\nSFINS")
						time.sleep(4)
						self.soc.shutdown(socket.SHUT_RDWR)
						self.soc.close()
				
				except socket.timeout:
					continue
				except socket.error:
					break
		def kill(self):
			with self.lock:
				self.dead = True




	def __init__(self, ip, port):
		self.ip = ip
		self.port = port
		
		threading.Thread.__init__(self)
		
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.soc.setblocking(False)
		self.soc.settimeout(1)
		self.lock = threading.Lock()
		self.dead = False
		self.clientList = []
		
		
	def bind(self):
		self.soc.bind((self.ip, self.port))
		self.soc.listen(5)
	
	
	def run(self):
		
		while True:
			
			with self.lock:
				if self.dead:
					break
			
			rmList = []
			for n in self.clientList:
				if not n.isAlive():
					rmList.append(n)
			for n in rmList:
				self.clientList.remove(n)
			
			
			try:
				soc, addy = self.soc.accept()
				newClient = self.ClientHandler(soc, addy)
				self.clientList.append(newClient)
				newClient.start()
				
				
			
			except socket.timeout:
				continue
			
			
			
		
		for n in self.clientList:
			n.kill()
		
		for n in self.clientList:
			n.join()
			
			
	def kill(self):
			with self.lock:
				self.dead = True


class Client(threading.Thread):
	def __init__(self, ip, port):
		threading.Thread.__init__(self)
		self.ip = ip
		self.port = port
		
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.lock = threading.Lock()
		#self.soc.setblocking(False)
		#self.soc.settimeout(1)
		self.dead = False
		
		self.totalDataSent = 0
		self.totalDataToSend = 0
		
	def connect(self):
	
		self.soc.connect((self.ip, self.port))
	
	def run(self):
		
		data = "X"*10000
		
		while True:
			with self.lock:
				if self.dead:
					break
			
			try:
				
				self.soc.send(data)
			
			except socket.timeout:
				continue
			
			self.totalDataSent += len(data)
		
			if self.totalDataToSend and self.totalDataToSend <= self.totalDataSent:
			
				break
		print self.soc.send("\r\nFIN")
		print self.soc.send("")
		
		self.soc.setblocking(False)
		self.soc.settimeout(1)
		c = 0
		while True:
			c +=  1
			if c > 10:
				print "Did not get SFINS back!"
				break
			try:
				d = self.soc.recv(1024)
				print "got",d
				if d[-5:] == "SFINS":
					break
			except socket.timeout:
				
				continue
			
		
		print self.soc.close()
		print "Closed"
	
	def kill(self):
		with self.lock:
			self.dead = True
			
			
				
		
