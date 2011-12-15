"""
This is the RX module :)
"""

import threading
import socket
import time
import sys

class RXTimer(threading.Thread):
	"""
	This ill be a thread that acts as a timer, and kills it
	"""

	def __init__(self, time, obj):
		threading.Thread.__init__(self)
		self.time = time
		self.timeremaining = time
		self.obj = obj
		self.isDead = False
	
	def run(self):
		timestart = time.time()
		timenow = time.time()
		while True:
			timeremain = self.time-(timestart-timenow)
			
			if self.isDead:
				break
			if timeremain > 0:
				if timeremain > 0.1:
					time.sleep(0.1)
				else:
					time.sleep(timeremain)
			else: #Less than zero 0.0
				break
		if not self.isDead:
			#Kill that motherfucker
			obj.stop()
			


class RX(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port

		self.TSFirst = 0
		self.TSLast = 0
		self.totalReceived = 0
		self.dataCount = 128000*10
		self.running = False
		self.isDead = False
		self.binded = False

		self.soc  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.setblocking(False)
		self.soc.settimeout(0.5)
		try:
			self.soc.bind(("", port))
			self.binded = True
		except:
			print "Unable to bind to the fudge"
		
			

	def run(self):

		while True:
			try:
				data, addr = self.soc.recvfrom(2048)
			except socket.timeout:
				#Timed out, check if we're dead?
				if self.isDead:
					break
				continue
			
			self.TSLast = time.time()
			if self.TSFirst == 0:
				print "First Blood!"
				self.TSFirst = self.TSLast
			self.totalReceived += len(data)
			
			if self.totalReceived >= self.dataCount:
				break

		#print speed!
		if self.TSLast == self.TSFirst:
			print "1 or 0 packets reeievd, can not determine data rate"
			return
		speed = self.totalReceived/(self.TSLast-self.TSFirst)
		print "Speed: ", speed
	
	def stop(self):
		"""
		This will flag the system it's dead and to stop :(
		"""
		self.isDead = True

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "./rx.py listen-port"
		sys.exit(-1)
	
	try:
		port = int(sys.argv[1])
	except:
		print "port isn't a numer?"
		sys.exit(-1)
	
	rxer = RX(port)
	if not rxer.binded:
		print "Quit due to non binded port"
		sys.exit(-1)
	rxer.start()

	while True:
		inp = raw_input("Press q to quit")
		if inp.lower() == "q":
			break
	rxer.stop()
	rxer.join()
	



