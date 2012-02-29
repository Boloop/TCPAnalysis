import NSClient 
import sys
import time

port = int(sys.argv[1])

print "create"
a = NSClient.NSClient()
print "Connect"
r = a.connect(("127.0.0.1", port))
if not r:
	print "Failed to Connect, TO"
	a.close()
	sys.exit(-1)
	
print "send"
a.send("Hello")
print "Sleeping"
time.sleep(3)

print "Connected, closing"
a.close()
print "closed"
