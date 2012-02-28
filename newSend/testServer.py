import NSListen
import socket
import sys

port = int(sys.argv[1])

print "Create"
a = NSListen.NSListen()
print "Bind"
try:
	a.bind(("127.0.0.1", port))
except socket.error:
	print "Couldn't bind :("
	sys.exit(-1)
print "start"
a.start()

print "listening..."
raw_input("Enter to quit")
a.isDead = True

print "Waiting to join"
a.join()
print "Ended"
