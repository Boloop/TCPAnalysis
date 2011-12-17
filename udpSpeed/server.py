

import SpeedPacket
import sys

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "./rx.py listen-port"
		sys.exit(-1)
	
	try:
		port = int(sys.argv[1])
	except:
		print "port isn't a numer?"
		sys.exit(-1)
		
	listener = SpeedPacket.SpeedListen(port)
	
	if not listener.binded:
		print "Quit due to non binded port"
		sys.exit(-1)
		
	listener.start()
	
	while True:
		inp = raw_input(">> ")
		inp = inp.lower()
		if inp == "q":
			break
		elif inp == "s":
			listener.printSummary()
		elif inp == "r":
			listener.reset()
	
	listener.stop()
	listener.join()
