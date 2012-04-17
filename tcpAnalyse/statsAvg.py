
import sys
import json

dataGroups = []

def matchesData(a, b):
	
	for akey in a.keys():
		if akey == "trialnum":
			continue
		
		if akey in b.keys():
			if not a[akey] == b[akey]:
				return False
		else:
			return False
	
	return True


if __name__ == "__main__":
	print "Will AVG json list?"
	
	
	###
	
	##aa = {"beb": False, "retrylimit": 10, "trialnum": 0, "droprate": 1.0, "congestioncontrol": "cubic"}
	##bb = {"beb": False, "retrylimit": 11, "trialnum": 1, "droprate": 1.0, "congestioncontrol": "cubic"}
	##print ">>", matchesData(aa, bb)
	##sys.exit(-1) 
	
	
	###
	if len(sys.argv) < 3:
		print "statsAvg.py [in-file] [out-file]"
		sys.exit(-1)
	
	infilepath = sys.argv[1]
	outfilepath = sys.argv[2]
	
	rttlimit = None
	if len(sys.argv) > 3:
		if "-RTT" in sys.argv:
			i = sys.argv.index("-RTT")
			rttlimit = float(sys.argv[i+1])*0.001
	
	print "Loading inFile"
	infile = open(infilepath, "r")
	indata = json.loads(infile.read())
	print "Loaded inFile!"
	accumconds = []
	for ddx in indata:
		dataconds = ddx[0]
		dataresult = ddx[1]
		
		#is dataconds in results
		index = None
		i = 0
		for rdatacond, tdatalist in accumconds:
			if matchesData(rdatacond, dataconds):
				index = i
				break
			i += 1
		if index == None: # Not in, add it in!
			accumconds.append( (dataconds, [dataresult] ) )
		else:
			accumconds[index][1].append(dataresult)
	
	print "Accumated Conditions"
	print len(indata), "vs", len(accumconds)
	print "Averaging"
	
	
	results = []
	
	for cond, datalist in accumconds:
		basekeys = {}
		for datal in datalist:
			#Check if all the keys are in
			for key in datal.keys():
				if not key in basekeys.keys():
					basekeys[key] = []
			
			#All keys in, append DATA
			for key in datal.keys():
			
				#If data None or below zero, ignore
				if datal[key] == None or datal[key] < 0:
					continue
					
				#If rttlimit!
				skip = False
				if key.startswith("RTT") and rttlimit != None:
					if datal[key] > rttlimit:
						skip = True
				if not skip: 
					basekeys[key].append(datal[key])
		
		#All data accumulated for condition, Average!
		
		dataavg = {}
		
		for key in basekeys.keys():
			dataavg[key] = float(sum(basekeys[key]))/float(len(basekeys[key]))
		
		results.append ( (cond, dataavg  ) )
	
	print "Finished Averaging, writing"
	
	jstring = json.dumps(results)
	
	jfile = open(outfilepath, "w")
	jfile.write(jstring)
	jfile.close()
			
			
			
		
	
	
	
	
	
	#Work out each test type....
