import sys
import json
import Gnuplot as gp

if __name__ == "__main__":
	if len(sys.argv) < 5:
		print "plotData.py [dataPath] [x-axis-key] [y-axis-key] [z-axis-key]"
		sys.exit(-1)
	
	datapath = sys.argv[1]
	xkey =  sys.argv[-3]
	ykey = 	sys.argv[-2]
	zkey =  sys.argv[-1]
	
	bebOnly = False
	retryLimit = None
	dropRate =  None
	
	ymax = None
	ymin = None
	
	if len(sys.argv) > 5:
		opts = sys.argv[1:-3]
		if "-beb" in opts:
			bebOnly = True
		
		
		if "-rl" in opts:
			retryLimit = int(opts[1+opts.index("-rl")])
		
		
		if "-dr" in opts:
			dropRate = int(opts[1+opts.index("-dr")])*0.1
			
		if "-yrange" in opts:
			ymin = float(opts[1+opts.index("-yrange")])
			ymax = float(opts[2+opts.index("-yrange")])
		
	
	print "BEB:", bebOnly, "RetryLimit:", retryLimit, "DropRate:", dropRate
			 
	
	
	
	
	print "Loading"
	datafile = open(datapath, "r")
	data = json.loads(datafile.read())
	print "Loaded"
	
	zdatagroup = {}
	#Get keys, enumerate
	for conds, data in data:
		r = conds[zkey]
		
		#Screen Data
		if bebOnly != None:
			if conds["beb"] != bebOnly:
				continue
		
		if retryLimit != None:
			if conds["retrylimit"] != retryLimit:
				continue
		
		if dropRate != None:
			if conds["droprate"] != dropRate:
				continue
		
		
		if not r in zdatagroup.keys():
			zdatagroup[r] = [(conds, data)]
		else:
			zdatagroup[r].append((conds, data) )
		
	
	#All the lines/yaxis grouped.. Now match X with Y list!
	plotdata = {}
	for key in zdatagroup.keys():
		datagroup = zdatagroup[key]
		
		xlist = []
		ylist = []
		
		for conds, data in datagroup:
			xlist.append(float(conds[xkey]))
			ylist.append(float(data[ykey]))
		
		#Got a list...
		
		xlistordered = xlist[:]
		xlistordered.sort()
		ylistordered = [None]*len(xlistordered)
		
		i = 0
		for x in xlistordered:
			indexy = xlist.index(x)
			
			yvalue = ylist[indexy]
			if ymax != None:
				if yvalue > ymax:
					yvalue = ymax
				elif yvalue < ymin:
					yvalue = ymin
			
			
			ylistordered[i] = yvalue
			i += 1
	
	
		plotdata[key] = (xlistordered, ylistordered)
	
	#Plot the data
	plot = gp.Gnuplot()
	plot.xlabel(xkey)
	plot.ylabel(ykey)
	
	lines = {}
	for cong in plotdata.keys():
		lines[cong] = gp.Data(plotdata[cong][0],plotdata[cong][1], with_="lines", title=str(cong))
	
	plot.plot(lines["reno"], lines["veno"], lines["cubic"], lines["westwood"])
	raw_input("letter to quit")
