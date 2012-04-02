import SSPack


print "create A+B"
a = SSPack.SSPack()
b = SSPack.SSPack()

a.ackNo = 10
a.sourceTS = 400
a.ackList = [8,0,5]

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
