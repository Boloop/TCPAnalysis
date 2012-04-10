import contClients
import time
import sys

print "Connect tcpDump"

tcpdump = contClients.tcpDumpClient()
tcpdump.nPort = 9014

softroute = contClients.softRouteClient()
softroute.nPort = 9014

sockettx = contClients.socketTXClient()
sockettx.nPort = 9016

if False:

	r = tcpdump.connect()
	if r:
		print "connected!"
	else:
		print "could not connect"
		sys.exit(-1)
	print "launch Listen Thread"
	tcpdump.launchListener()
	print "set File"
	tcpdump.changeFileName("newnewFILE")

	print "Run program"
	tcpdump.execute()
	print "running sleep"
	time.sleep(5)
	print "isRunning?"
	print tcpdump.isRunning()
	print "kill"
	tcpdump.kill()
	print "isRunning?"
	print tcpdump.isRunning()
	print "close again"
	tcpdump.close()
	
if False:
	print "running SOFTROUTE"
	r = softroute.connect()
	if r:
		print "connected!"
	else:
		print "could not connect"
		sys.exit(-1)
	print "launch Listen Thread"
	softroute.launchListener()
	print "Set drop rate"
	softroute.changeDataRate(100)
	print "Execute"
	softroute.execute()
	time.sleep(5)
	print "isRunning?"
	print softroute.isRunning()
	print "kill"
	softroute.kill()
	print "isRunning?"
	print softroute.isRunning()
	print "close again"
	softroute.close()

if False:
	print "running socketTX"
	r = sockettx.connect()
	if r:
		print "connected!"
	else:
		print "could not connect"
		sys.exit(-1)
	print "launch Listen Thread"
	sockettx.launchListener()
	print "Set drop rate"
	sockettx.changeCongestion("reno")
	print "Execute"
	sockettx.execute()
	i = 0
	while i < 20:
		print "i", i
		if sockettx.isRunning():
			time.sleep(1)
			i += 1
		else:
			break
	print "isRunning?"
	print sockettx.isRunning()
	if sockettx.isRunning():
		print "kill"
		sockettx.kill()
	print "isRunning?"
	print sockettx.isRunning()
	print "close again"
	sockettx.close()






if True:
	#Connect to each service!
	tcpdump.sIP = "192.168.0.42"
	softroute.sIP = "192.168.0.41"
	sockettx.sIP = "192.168.0.42"
	r = tcpdump.connect()
	if r:
		print "connected tcpdump!"
	else:
		print "could not connect tcpdump"
		sys.exit(-1)
		

	r = softroute.connect()
	if r:
		print "connected softroute!"
	else:
		print "could not connect softroute"
		tcpdump.close()
		sys.exit(-1)
	
	r = sockettx.connect()
	if r:
		print "connected sockettx!"
	else:
		print "could not connect sockettx"
		tcpdump.close()
		softroute.close()
		sys.exit(-1)
		
	print "check and kill all tasks"
	
	for droprate in [1, 100]:
		#Set the drop rate!
		pass
		
	print "closing connections"
	tcpdump.close()
	softroute.close()
	sockettx.close()
	print "closed them all!"
	
