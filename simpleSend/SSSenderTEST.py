import SSSender
import SSPack
import time

def onSend(dataList=[]):
	def _onSend(pack):
		print "Sending Pack: "+str(pack)+" TS:"+str(pack.sourceTS)
		dataList.append(pack)
	return _onSend



def ackWire(dataList=[]):
	"""
	Will return a list of SSPacks to send back!
	"""
	
	for d in dataList:
		#d.seg
		pass


class timer():
	def __init__(self):
		self.timeval = 0.0
	def getTime(self):
		return self.timeval 
	
	def add(self, val):
		self.timeval += val
	def __iadd__(self, other):
		self.add(other)
		return self

onSWire = []

s = SSSender.SSSender()
t = timer()
s.sendCall = onSend(dataList=onSWire)
s.timeNow = t.getTime
s.rtTimer.timeNow = t.getTime
print s
print "SoW"+ str(s.segsOnWire())
print "Send First Segment"
s.sendOnIdle()
print s
print "SoW"+ str(s.segsOnWire())
print
print 
print "Ack First Segment"
t += 1
print t.timeval
p = SSPack.SSPack()
p.ackNo = 0
p.lastDestinationTS = 0
s.onAck(p)
print s
print "SoW"+ str(s.segsOnWire())
print
print
##
# Ack both Segs onWire
##
while len(onSWire):
	onSWire.pop()

print "Ack 1+2 Segment"
p = SSPack.SSPack()
p.ackNo = 1
p.lastDestinationTS = t.getTime()

q = SSPack.SSPack()
q.ackNo = 2
q.lastDestinationTS = t.getTime()
pt = t.getTime()
t += 1.1
print "Echo t", pt, "read t", t.getTime()
s.onAck(p)
s.onAck(q)

print s
print "SoW"+ str(s.segsOnWire())

##
# Ack Packets
##
print "Acking all on Wire"
acklist = []
for pa in onSWire:
	p = SSPack.SSPack()
	p.ackNo = pa.segNo
	p.lastDestinationTS = t.getTime()
	acklist.append(p)

while len(onSWire):
	onSWire.pop()
t += 1.1

for ap in acklist:
	s.onAck(ap)
print s
print "SoW"+ str(s.segsOnWire())

##
# Window size now 8...
##
print "Partial Ack" 
print "before: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()

print "Ack 8, ignore 7..."
p = SSPack.SSPack()
p.ackNo = 6
p.ackList = [8]
p.lastDestinationTS = t.getTime()
t += 1.2
s.onAck(p)
print "After 1: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()
print s
print "SoW"+ str(s.segsOnWire())
print 

print "Ack 9, ignore 7..."
p = SSPack.SSPack()
p.ackNo = 6
p.ackList = [8, 9]
p.lastDestinationTS = t.getTime()
t += 1.3
s.onAck(p)
print "After 2: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()
print s
print "SoW"+ str(s.segsOnWire())
print 

print "Ack 10, ignore 7..."
p = SSPack.SSPack()
p.ackNo = 6
p.ackList = [8, 9, 10]
p.lastDestinationTS = t.getTime()
t += 1.3
s.onAck(p)
print "After 3: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()
print s
print "SoW"+ str(s.segsOnWire())
print 

##
# Printed to be In FAST_RECOVERY!
##

print "Ack 11, ignore 7..."
p = SSPack.SSPack()
p.ackNo = 6
p.ackList = [8, 9, 10, 11]
p.lastDestinationTS = t.getTime()
t += 1.3
s.onAck(p)
print "After 4: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()
print s
print "SoW"+ str(s.segsOnWire())
print 

print "Ack 12, ignore 7..."
p = SSPack.SSPack()
p.ackNo = 6
p.ackList = [8, 9, 10, 11, 12]
p.lastDestinationTS = t.getTime()
t += 1.3
s.onAck(p)
print "After 5: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()
print s
print "SoW"+ str(s.segsOnWire())
print 

print "Ack 7"
p = SSPack.SSPack()
p.ackNo = 12
p.ackList = []
p.lastDestinationTS = t.getTime()
t += 1.3
s.onAck(p)
print "After 6: la:", s.lastAck, "dac", s.duplicateAckCount, "oW:", s.segsOnWire()
print s
print "SoW"+ str(s.segsOnWire())
print 

print "Sleep for 5"
time.sleep(5)
t += 10 # Cause a timeout 
print "Sleep for 5, Cause TO"
time.sleep(5)
print s
print "DELETING"
s.__del__()
