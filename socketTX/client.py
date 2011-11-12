import socketTX
import socket
import sys
import time

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print " please have [ip] [port] to listen to"
		sys.exit()
		
	ip = sys.argv[1]
	timeout = 30
	slept = 0
	try:
		port = int(sys.argv[2])
	except:
		print "Are you sure that is a port number?"
		sys.exit()
	
	print "Trying "+ip+":"+str(port)
	
	client = socketTX.Client(ip, port)
	client.totalDataToSend = 1000*1024*1024 #1MB
	
	try:
		client.connect()
	except socket.error, why:
		print "Could not conect due to:", why
		sys.exit()
		
	client.start()
	while True:
		time.sleep(0.5)
		slept += 0.5
		if not client.isAlive():
			print "Sent All data"
			break
		elif slept >= timeout:
			print "Timed out"
			break
	
	client.kill()
	
	client.join()
	
