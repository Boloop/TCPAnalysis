
import SSPack
import SSSender
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
		udpCall(pack.data)
	
	return _wrapThenSend



print "Making UDP socket and Send class"
u = UDPWrapper.sender("127.0.0.1", 9050)
s = SSSender.SSSender()

print "Binding Calls"
u.onPacket = unWrapOnReceive(s.onAck)
s.sendCall = wrapThenSend(u.send)

print "Running UDP thread, sleep for 3"
u.start()
time.sleep(3)
print "Send Initial Packet!"
s.sendOnIdle()

print "sleep for 10"
time.sleep(10)

s.__del__()
u.close()
