import UDPWrapper
import sys
import time

print "Make sender"
a = UDPWrapper.sender("127.0.0.1", 9055)
print "start rcvr"
a.start()

print "Send"
a.send("Hello")

print "Sleep"
time.sleep(5)
print "sleep over"
a.close()


