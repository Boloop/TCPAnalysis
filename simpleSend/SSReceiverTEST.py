import SSReceiver
import SSPack

def onSend(dataList=[]):
	def _onSend(pack):
		print "Sending Pack: "+str(pack)
		dataList.append(pack)
	return _onSend



ackList = []
pl = "F"*1400
r = SSReceiver.SSReceiver()
r.sendCall = onSend(dataList=ackList)
print r

print "First Seg"
p = SSPack.SSPack()
p.segNo = 0
p.payload = pl
p.sourceTS =1 
print p
r.onSegment(p)
print r

print "Third Seg (skip 2nd)"
p = SSPack.SSPack()
p.segNo = 2
p.payload = pl
p.sourceTS =2 
print p
r.onSegment(p)
print r

print "Forth Seg (skip 2nd)"
p = SSPack.SSPack()
p.segNo = 3
p.payload = pl
p.sourceTS =3 
print p
r.onSegment(p)
print r

print "Sixth Seg (skip 2nd, 5th) also TS = 2"
p = SSPack.SSPack()
p.segNo = 5
p.payload = pl
p.sourceTS = 2 
print p
r.onSegment(p)
print r

print "Ack 2nd, shuld give ack 4th! (number 3?)"
p = SSPack.SSPack()
p.segNo = 1
p.payload = pl
p.sourceTS =5 
print p
r.onSegment(p)
print r

print "Send Dupe seg 6"
p = SSPack.SSPack()
p.segNo = 5
p.payload = pl
p.sourceTS =5 
print p
r.onSegment(p)
print r

print 
