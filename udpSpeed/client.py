
import sys
import SpeedPacket


if __name__ == "__main__":
	packetsize = 1400
	datasent = 2000
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
		
	txer = SpeedPacket.SpeedSend(port, host)
	txer.setDataRate(datasent)
	txer.setPacketSize(packetsize)
	
	txer.fire()
