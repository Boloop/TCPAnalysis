import socLis
import time
import sys


def onK(s, args):
	s.soc.send("K: "+str(args)+"\r\n")


print "Start"
l = socLis.Listen()
l.commands.append("K")
l.commandactions.append(onK)
if l.soc == None:
	print "Failed to listen...."
	sys.exit(-1)
l.start()
raw_input( "stop?")
l.kill()

