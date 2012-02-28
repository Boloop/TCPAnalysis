import NSClient 
import sys

port = int(sys.argv[1])

print "create"
a = NSClient.NSClient()
print "Connect"
r = a.connect(("127.0.0.1", port))
if not r:
	print "Failed to Connect, TO"
	sys.exit(-1)
print "Connected, closing"
a.close()
print "closed"
