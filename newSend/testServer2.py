import NSListen
import socket
import sys
import time

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



print "Got a connection, sending it a lot of Data!"

cli = accl[0]
if True:
	while 1:
		print "sending"
		cli.send("Hello"*2000)
		time.sleep(10)

	
	

print "Killing connections"
for b in accl:
	print "killing", b
	b.close()

print "killed all"
a.isDead = True
print "Waiting to join"
a.join()
print "Ended server"

