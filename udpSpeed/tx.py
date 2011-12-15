"""
this will be responsible for Transmitting data
"""
import socket
import time
import sys

class TX(object):

	def __init__(self, ip, port):
		self.port = port
		self.ip = ip
		print "P", port, " ip", ip
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.soc.connect((ip, port))
		self.datasize = 1400
		self.datarate = 128000000
	
		self.time = 20
	
	def fire(self):

		#figure out packetrate to send
		packetrate = float(self.datarate)/self.datasize
		packetperiod = 1/packetrate

		pdata = "X"*self.datasize

		starttime = time.time()
		timenow = time.time()
		while timenow-starttime < self.time:
			#print "send"
			self.soc.send(pdata)
			timenownow = time.time()
			sleeptime = packetperiod-timenownow+timenow
			if sleeptime > 0:
				time.sleep(sleeptime)
			timenow = timenownow



if __name__ == "__main__":
	packetsize = 1400
	datasent = 2
	if len(sys.argv) < 3:
		print "./tx.py ip port"
		sys.exit(-1)
	if len(sys.argv) == 3:
		try:
			port = int(sys.argv[2])
		except:
			print "Invalid Port"
			sys.exit(-1)
		host = sys.argv[1]
	elif len(sys.argv) == 5:
		try:
			port = int(sys.argv[4])
		except:
			print "Invalid Port"
			sys.exit(-1)
		host = sys.argv[3]

		try:
			packetsize = int(sys.argv[1])
			datasent = int(sys.argv[2])
		except:
			print "Invalid packetsize and/or datasent"
			sys.exit(-1)

	else:
		print "./tx.py [packetsize] [speed] ip port"
		sys.exit(-1)

	txer = TX(host, port)
	print "firing"
	txer.fire()
	print "fired"
