import NSListen
import socket
import sys

port = int(sys.argv[1])

accl = []

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


print "Accepting Connections in 10 seconds"
while 1:
	r = a.accept(10)
	if r:
		print r
		accl.append(r)
		break
	else:
		print "no connection"
		break



print "Got a connection, wait for data to recv"
if len(accl) > 0:
	while 1:
		c = accl[0].read(5)
		print "Recv", c
		if not c:
			break 

print "Killing connections"
for b in accl:
	print "killing", b
	b.close()

print "killed all"
a.isDead = True
print "Waiting to join"
a.join()
print "Ended server"

