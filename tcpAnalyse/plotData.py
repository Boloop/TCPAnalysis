import sys
import json
import Gnuplot as gp

def plotData(xkey, ykey, zkey, dataset, ymax=None, ymin=None, bebOnly=False, retryLimit=None, dropRate=None, rescaleX=True):
	"""
	will return gnu plot 
	"""
	zdatagroup = {}
	#Get keys, enumerate
	for conds, data in dataset:
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
	
		
		#Rescale xAxis
		if retryLimit != None and rescaleX:
			for i in xrange(len(xlistordered)):
				xlistordered[i] = 100.0*((xlistordered[i]/100.0)**retryLimit)
		
		plotdata[key] = (xlistordered, ylistordered)
	
	#Plot the data
	plot = gp.Gnuplot()
	plot.xlabel(xkey)
	plot.ylabel(ykey)
	
	lines = {}
	for cong in plotdata.keys():
		lines[cong] = gp.Data(plotdata[cong][0],plotdata[cong][1], with_="lines", title=str(cong))
	
	print "itemlistlen", len(plot.itemlist)
	for akey in lines.keys():
		plot.itemlist.append(lines[akey])
	
	return plot

if __name__ == "__main__":

	drawAll = False
	if len(sys.argv) < 5:
		if len(sys.argv) == 3 and sys.argv[2] == "-da":
			drawAll = True
		else:
			print "plotData.py [dataPath] [x-axis-key] [y-axis-key] [z-axis-key]"
			sys.exit(-1)
	
	
	datapath = sys.argv[1]
	
	if len(sys.argv) > 5:
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
	
	#Plot it?
	if not drawAll:
		plot = plotData(xkey, ykey, zkey, data, ymax=ymax, ymin=ymin, bebOnly=bebOnly, retryLimit=retryLimit, dropRate=dropRate)
	
		plot.hardcopy('dtet.png',terminal = 'png')
		plot.replot()
		#plot.plot(lines["reno"], lines["veno"], lines["cubic"], lines["westwood"])

		raw_input("letter to quit")
	
	else:
		print "Draw all..."
		
		for xkey in ["droprate"]:
			for ykey in ["TIME", "RTTavg", "RTTmax", "RTTmin", "CONGavg", "RETRANSpercent", "DATAtotal", "DATAoverall", "RETRANScount"]:
			
				
				if xkey == "droprate":
					retryLimit = 1
					
				if ykey.startswith("RTT"):
					ymin = 0
					if ykey == "RTTavg":
						ymax = 0.15
					else:
						ymax = 0.5
				else:
					ymin = None
					ymax = None
					
				#try:
				retryLimit = 3
				plot = plotData(xkey, ykey, "congestioncontrol", data, ymax=ymax, ymin=ymin, bebOnly=bebOnly, retryLimit=retryLimit, dropRate=dropRate)
				#except:
				#	continue
				ss = "plot_y_"+ykey+"_rl_"+str(retryLimit)
				plot.set_range("xrange", (0,50))
				
				if ykey == "RETRANSpercent":
					plot.set_range("yrange", (0,40))
				elif ykey == "TIME":
					plot.set_range("yrange", (0,45))
				elif ykey == "CONGavg":
					plot.set_range("yrange", (1500,4000))
				elif ykey == "RTTavg":
					plot.set_range("yrange", (0.05,0.16))
				plot.hardcopy(ss+'.png',terminal = 'png')
				plot.close()
		
