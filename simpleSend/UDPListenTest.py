

import UDPWrapper
import sys
import time

def rcvMsg(a):
	def _rcvMsg(p):
		print "Sending back message"
		a.send(p)
	return _rcvMsg

print "Trying to bind to port 9005"

a = UDPWrapper.listen(9055)
a.onPacket = rcvMsg(a)
if not a.binded:
	print "Failed to bind"
	sys.exit()
else:
	print "Binded!"

a.start()

time.sleep(10)	
a.close()
