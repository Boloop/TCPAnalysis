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
	tcpdump.nIP = "192.168.0.42"
	softroute.nIP = "192.168.0.41"
	sockettx.nIP = "192.168.0.42"
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
		
	print "Running Listening Threads"
	tcpdump.launchListener()
	softroute.launchListener()
	sockettx.launchListener()
	
	print "check and kill all tasks"
	if tcpdump.isRunning():
		print "killing tcpdump"
		tcpdump.kill()
	else:
		print "tcpDump, standing by"
		
	if softroute.isRunning():
		print "killing softroute"
		softroute.kill()
	else:
		print "softroute, standing by"
		
	if sockettx.isRunning():
		print "killing sockettx"
		sockettx.kill()
	else:
		print "sockettx, standing by"	
	
	
	
	trials = 3
	print "running", trials, "trials per test!"
	for droprate in [1, 100, 1000]:
		#Set the drop rate!
		print "Setting DataRate"
		softroute.changeDataRate(100000)
		print "Setting DropRate to", droprate
		softroute.changeDropRate(droprate)
		print "Executing softroute"
		softroute.execute()
		time.sleep(10)
		for cong in ["reno", "cubic"]:
			for trialnum in xrange(trials):
				print "Droprate:", droprate, "cong:", cong, "TrialNum:", trialnum
				tcps = "data_dr"+str(droprate)+"_c_"+cong+"_t_"+str(trialnum)
				tcpdump.changeFileName(tcps)
				tcpdump.execute()
				time.sleep(1)
				
				sockettx.changeCongestion(cong)
				sockettx.execute()
				i = 0
				while i < 120:
					#print "i", i
					if sockettx.isRunning():
						time.sleep(1)
						i += 1
					else:
						break
				
				if sockettx.isRunning():
					print "TO"
					sockettx.kill()
				else:
					print "Not TO"
				
				tcpdump.kill()
		
		softroute.kill()
		
	print "closing connections"
	tcpdump.close()
	softroute.close()
	sockettx.close()
	print "closed them all!"
	
