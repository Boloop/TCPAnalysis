import contClients
import time
import sys

print "Connect tcpDump"

tcpdump = contClients.tcpDumpClient()
tcpdump.nPort = 9014
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

