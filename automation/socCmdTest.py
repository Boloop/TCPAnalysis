import socCmd
import sys
import time

print "Creata"
a = socCmd.socCmd()
a.nPort = 9014

print "connecting"
r = a.connect()
if r:
	print "connected!"
else:
	print "could not connect"
	sys.exit(-1)
	
print "Disconnect"
a.close()

print "restart"
a = socCmd.socCmd()
a.nPort = 9014
print "connecting"
r = a.connect()
if r:
	print "connected!"
else:
	print "could not connect"
	sys.exit(-1)

print "launch Listen Thread"
a.launchListener()

print "Call, is running"
a.callIsRunning()
print "Wait for response"
r = a.lThread.waitFor("IR")
print "response:", r
time.sleep(1)
print "close again"
a.close()

