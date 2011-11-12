import socketTX
import socket
import sys


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print " please have [ip] [port] to listen to"
		sys.exit()
		
	ip = sys.argv[1]
	try:
		port = int(sys.argv[2])
	except:
		print "Are you sure that is a port number?"
		sys.exit()
	
	print "Trying "+ip+":"+str(port)
	
	server = socketTX.Server(ip,port)
	try:
		server.bind()
	except socket.error, why:
		print "Could not bind due to:", why
		sys.exit()
	
	server.start()
	
	raw_input("press enter to quit")
	
	server.kill()
	
	server.join()
