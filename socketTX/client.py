import socketTX
import socket
import sys
import time


def getArgPair(flag, args, quit=True):
	"""
	This will scan the list of args and return timeout value,
	None means invalid.
	True means not present.
	will remove args from list!
	"""
	
	i = 0
	for n in args:
		if n == flag:
			if len(args) <= i+1:
				#invalid number of args
				if quit:
					print "flag", flag, "is missing it's agument. Quitting :("
					sys.exit()
				return True
			val = args[i+1]
			#Remove from args
			args.pop(i)
			args.pop(i)
			return val
			
		i += 1
	return None

def makeInt(val, flag):
	"""
	Will return int from string, if fail, print error and quit
	For parsing commandline args!
	"""
	
	try:
		result = int(val)
	except:
		print "Could not parse flag", flag, "Quiting :("
		sys.exit()
	return result

def makeIntUnit(val, flag):
	"""
	Will parse ints with strings like 10M = 10000000 126K = 126000 etc...
	"""
	
	try:
		unit = val[-1]
		#is number?
		if "0" <= unit <= "9":
			return int(val)
		
		if unit == "k":
			result = 1000
		elif unit == "M":
			result = 1000000
		else:
			print "Unknown unit for flag", flag,"with",unit
			sys.exit()
		
		result *= int(val[:-1])
	except:
		print "Could not parse flag", flag
		sys.exit()
	
	return result

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print " please have [ip] [port] to listen to"
		sys.exit()
	
	
	args = sys.argv[1:-2]
	
	st = getArgPair("-t", args)
	datas = getArgPair("-d", args)
	if st:
		timeout = makeInt(st, "-t")
	else:
		timeout = 30
	
	if datas:
		dataamount = makeIntUnit(datas, "-d")
	else:
		dataamount = 200000
	
	print "timeout     : {0}".format(timeout)
	print "Data to send: {0}".format(dataamount)

	
	
	ip = sys.argv[-2]
	timeout = 30
	slept = 0
	try:
		port = int(sys.argv[-1])
	except:
		print "Are you sure that is a port number?"
		sys.exit()
	
	print "Trying "+ip+":"+str(port)
	
	client = socketTX.Client(ip, port)
	client.totalDataToSend = dataamount
	
	
	try:
		client.connect()
	except socket.error, why:
		print "Could not conect due to:", why
		sys.exit()
		
	client.start()
	while True:
		time.sleep(0.5)
		slept += 0.5
		if not client.isAlive():
			print "Sent All data"
			break
		elif slept >= timeout:
			print "Timed out"
			break
	
	client.kill()
	
	client.join()
	
