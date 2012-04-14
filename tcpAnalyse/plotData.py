import sys
import json
import Gnuplot as gp

if __name__ == "__main__":
	if len(sys.argv) < 5:
		print "plotData.py [dataPath] [x-axis-key] [y-axis-key] [z-axis-key]"
		sys.exit(-1)
	
	datapath = sys.argv[1]
	xkey =  sys.argv[2]
	ykey = 	sys.argv[3]
	zkey =  sys.argv[4]
	
	print "Loading"
	datafile = open(datapath, "r")
	data = json.loads(datafile.read())
	print "Loaded"
	
	zdatagroup = {}
	#Get keys, enumerate
	for conds, data in data:
		r = conds[zkey]
		
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
			ylistordered[i] = ylist[indexy]
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
