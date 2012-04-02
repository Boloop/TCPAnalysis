import SSSender
import time

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

def RTOCall(timer):
	def _RTOCall():
		print "Timed at time:", timer()
	return _RTOCall

rt = SSSender.RTTimer()
t = timer()
rt.timeNow = t.getTime
rt.rtoCall = RTOCall(t.getTime)

print "Init"

print "Run thread..."
rt.start()

print "Setting to timeout on 10"
rt.reset(10.0)
print "Sleeping for 4 seconds"
time.sleep(4)
print "set time to 10 and sleep for 5 seconds"
t.timeval = 10.1
time.sleep(5)

print "reset Timer to 13 sleep for 5"
rt.reset(13.0)
time.sleep(5)

print "set time to 13.1, sleep 5"
t.timeval = 13.1
time.sleep(5)
print "Kill thread"
rt.dead = True
rt.join()
