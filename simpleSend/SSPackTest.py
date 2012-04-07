import SSPack


print "create A+B"
a = SSPack.SSPack()
b = SSPack.SSPack()

a.ackNo = 10
a.sourceTS = 400
a.ackList = [8,0,5]
a.compressor = False
b.compressor = False

print "print a, b"
print "A: "+str(a)
print "B: "+str(b)
print "A==B", a == b
print "Make A data"
a.make()
print "A is Made, Feed into B"
b.read(a.data)
print "print a, b"
print "A: "+str(a)
print "B: "+str(b)
print "A==B", a == b
print
print "Change ackList"
a.ackNo = 10
a.ackList = [3, 5,6,7, 9 ]
print a.ackList
print "Compress"
a.ackListToR()
print a.rackList
print "Decompress"
a.rackToAckList()
print a.ackList
print
print
print "recompile A with Compressor on"
a.compressor = True
b.compressor = True
print "Compile a"
a.make()
print a.rackList
print "Feed Data into B"
b.read(a.data)
print "A read!"
print b.ackList
