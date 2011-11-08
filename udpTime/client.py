import UDPTime
import sys

ip = sys.argv[1]
port = int(sys.argv[2])

c = UDPTime.Client(ip, port, 122, 40)

c.start()

c.join()

print "TO", c.timedout
print "stage", c.stage

print c.dpkt.t1
print c.dpkt.t2
print c.dpkt.t3
print c.dpkt.t4
