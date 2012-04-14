"""
This file 
"""

import tcpStats
import sys
import json

def decodeFileName(fn):
	"""
	this will return a dic of settings the file went under
	"""
	result = {}
	result["droprate"] = 0.0
	fnc = fn.split("_")
	
	for sc in fnc:
		if sc.startswith("dr"):
			result["droprate"] = 0.1*int(sc[2:])
	
	if "beb" in fnc:
		result["beb"] = True
	else:
		result["beb"] = False
	
	if "rl" in fnc:
		i = fnc.index("rl")
		result["retrylimit"] = int(fnc[i+1])
	else:
		result["retrylimit"] = 1
	
	if "c" in fnc:
		i = fnc.index("c")
		result["congestioncontrol"] = fnc[i+1]
	else:
		result["congestioncontrol"] = "unknown"
	
	if "t" in fnc:
		i = fnc.index("t")
		result["trialnum"] = int(fnc[i+1])
	else:
		result["trialnum"] = -1
	
	return result


if __name__ == "__main__":
	#Do your magic
	files = sys.argv[1:]
	stats = []
	for f in files:
		fs = f.split("/")
		fn = fs[-1]
		if not fn.startswith("data"):
			continue
			
		print "Processing", fn
		filesettings = decodeFileName(fn)
		tcpcon = tcpStats.loadPcap(f)
		if tcpcon == None:
			print "Error Reading?"
			continue
		tcpcon.setOrigin()
		tcpcon.removeFIN()
		tcpstat = tcpStats.TcpStat(tcpcon)
		result = tcpstat.getDic()
		
		stats.append( (filesettings, result) )
	
	print "Generating JSON"
	jstring = json.dumps(stats)
	
	jfile = open("stats", "w")
	jfile.write(jstring)
	jfile.close()
	print "TaDa!"
		
		
