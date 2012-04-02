
import SSPack
import SSReceiver
import UDPWrapper
import time 

def unWrapOnReceive(SScall):
	def _unWrapOnReceive(pack):
		p = SSPack.SSPack()
		p.read(pack)
		SScall(p)
	
	return _unWrapOnReceive

def wrapThenSend(udpCall):
	def _wrapThenSend(pack):
		pack.make()
		
		time.sleep(0.25)
		print "SENDSENDSENDSEND"
		udpCall(pack.data)
	
	return _wrapThenSend



print "Making UDP socket and Reciever class"
u = UDPWrapper.listen(9050)
s = SSReceiver.SSReceiver()

print "Binding Calls"
u.onPacket = unWrapOnReceive(s.onSegment)
s.sendCall = wrapThenSend(u.send)

print "Running UDP thread, sleep for 10"
u.start()
time.sleep(3)



time.sleep(10)

print "Close "

#s.__del__()
u.close()
