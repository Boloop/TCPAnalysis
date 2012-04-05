import PcapReader as pcr
import TcpMon as tm
import sys
import Gnuplot as gp
import dpkt
import struct

def strIP(ipadd):
	"""
	Will convert to binary to spit out an int of the address
	"""
	a,b,c,d = struct.unpack("BBBB", ipadd)
	return str(a)+"."+str(b)+"."+str(c)+"."+str(d)

def hasFlag(flag, args):
	"""
	This will return a boolean if the flag is present in the list.
	"""
	
	return flag in args

def flagWithX(flag, x, args):
	"""
	This will find flag and return the number of parameters x
	after it
	e.g. -t 10 20 will be ("-t", 2) and return "10" and "20"
	
	return None if flag not there, False if incorrect number of elements
	"""
	if not hasFlag(flag, args):
		return None
	pass
	
	i = args.index(flag)
	
	if len(args) < i+x:
		return False
	
	return args[i:i+x]
	
	
	

def tcpStat(tcp):
	"""
	Will return a string of stat info
	"""
	sa = ""
	if tcp.flags & dpkt.tcp.TH_SYN:
		sa += "SYN"
	if tcp.flags & dpkt.tcp.TH_ACK:
		sa += "ACK"
	
	return "S:"+str(tcp.seq)+" A:"+str(tcp.ack)+" "+sa+" len:"+str(len(tcp.data))

if __name__ == "__main__":


	if hasFlag("-h", sys.argv[1:]):
		print "Help!"
		print " -cong        show congestion"
		print " -rtt(ts)     show round trip time"
		print " -data        show dataTXrate/throughoutput"
		sys.exit()
	
	if len(sys.argv) < 2:
		print "Please ensure you have got [path]"
		sys.exit()
	args = sys.argv[1:-1]
	
	showCong = hasFlag("-cong", args)
	showRTT = hasFlag("-rtt", args)
	showRTTTS = hasFlag("-rttts", args)
	showDataTX = hasFlag("-data", args)
	
	showECN = hasFlag("-ecn", args)
	
	path = sys.argv[-1]
	
	p = pcr.PcapRead()
	if not p.open(path):
		print "whoops?"
		#print ("Incorrect header. :( magic number was {:x}".format(p.magicNumber))
		
	
	
	print "Pcap file open details:"
	print "R: {0} V:{1}.{2} NetType: {3}".format( p.reversed, p.versionNumberMajor, p.versionNumberMinor, p.netType) 
	
	if p.netType != pcr.LL_ETHERNET and p.netType != pcr.LL_LINUX_SLL:
		print "Does not support this Link Type :( QUITTING"
		sys.exit() 
	
	#get filename?
	fn = path.split("/")[-1]
	
	
	tcpCon = None
	
	
	
	while 1:
		packet = p.nextPack()
		if not packet:
			print "EOF"
			break
		
			
			
		#Lets find out what it's made of!
		if   p.netType == pcr.LL_ETHERNET:
			eth = dpkt.ethernet.Ethernet(packet.pData)
		elif p.netType == pcr.LL_LINUX_SLL:
			eth = dpkt.ethernet.Ethernet(packet.pData[2:]) # Hacks, lol. Just don't try to read the ethernet 
								       # frame. Addys wrong, but ethertype right!
								       # http://www.tcpdump.org/linktypes/LINKTYPE_LINUX_SLL.html
		
		#Is it an IP packet, yeah?
		if type(eth.data) == type(dpkt.ip.IP()):
			#It is, It is an ip packet!
			ip = eth.data
			if type(ip.data) == type(dpkt.tcp.TCP()):
				#it's TCP
				#Lock And load
				if tcpCon == None:
					tcpCon = tm.TcpCon(ip, packet.time)
					
				elif tcpCon.sameSocket(ip):
					tcpCon.addIPPacket(ip, packet.time)
					#tcpCon.addPacket(ip.data, packet.time)
					#print "Yay"
				else:
					print "Nay"
			
					
				
		
		
		#print packet.time, packet.pLen
	
	print "File loaded"
	
	if tcpCon:
	
		tcpCon.setOrigin()
		tcpCon.removeFIN()
		#Print stats
		ipa = strIP(tcpCon.ip1)+":"+str(tcpCon.port1)
		ipb = strIP(tcpCon.ip2)+":"+str(tcpCon.port2)
		print ipa+" >>  FORWARD  >> "+ipb+" ["+str(len(tcpCon.forward))+"]["+str(len(tcpCon.forwardECN))+"]"
		print ipa+" <<  BACKWARD << "+ipb+" ["+str(len(tcpCon.backward))+"]["+str(len(tcpCon.backwardECN))+"]" 
		count = tcpCon.getPacketCount()
		drop = count/100
		drop = 4
		print "has {0} packets, dropping last {1}".format(count, drop)
		drop = -1-drop
		
		tdata, tdif = tcpCon.getTXRate()
		print "{0} bytes sent over {1}secs at {2}bytes/sec".format(tdata, tdif, tdata/tdif)
		ecenum = tcpCon.countFlags(dpkt.tcp.TH_ECE)
		print "Has {0} flagged ECE bits".format(ecenum)
		cwrnum = tcpCon.countFlags(dpkt.tcp.TH_CWR)
		print "Has {0} flagged CWR bits".format(ecenum)
		
		path = tm.PATH_FORWARD
		cenum = tcpCon.countECNInIP(tm.ECN_CE, path=path)
		print "Has {0} flagged CE bits".format(cenum)
		ect0num = tcpCon.countECNInIP(tm.ECN_ECT0, path=path)
		print "Has {0} flagged ECT0 bits".format(ect0num)
		ect1num = tcpCon.countECNInIP(tm.ECN_ECT1, path=path)
		print "Has {0} flagged ECT1 bits".format(cenum)
		nonectnum = tcpCon.countECNInIP(tm.ECN_NONECT, path=path)
		print "Has {0} flagged NON-ECT bits".format(nonectnum)
		
		#sN = tcpCon.getSACKs()
		#print "Has {0} SACK opt'ed packs".format(sN)
		#sys.exit()
		
		if showCong:
			#Congestion Window
			wints, winwin = tcpCon.unackdPackets()
			wints, winwin = (wints[:drop],winwin[:drop])
			wints += [wints[-1]]
			winwin += [0]
			congwinplot = gp.Gnuplot()
			congwinplot.xlabel("time")
			congwinplot.ylabel("Congestion Window size")
			print "ok", wints[-1],winwin[-1]
			congwindata = gp.Data(wints,winwin, with_="filledcurves", title="Congestion Window")
		
			rtsts, rtsrts, l = tcpCon.getRetransmits()
		
			#Santa has a sack (of toys)
			sacks = tcpCon.getSACKs()
			sacksackts = []
			sacksack = []
			sackendts = []
			sackend = []
			segsize = 1388
			for ts, ack, segs in sacks:
				unacks = segs[0]
				unacksegs = unacks/segsize
				if unacksegs < 1:
					unacksegs = 0
				#add unacks
				for x in xrange(0, unacksegs):
					sacksackts.append(ts)
					sacksack.append(x*segsize)
				#addlatest ack'd
				sackendts.append(ts)
				sackend.append(segs[-1])
			
			
			#Ecn!
			ecncets = [0]
			ecnceval = [100]
			if showECN:
				ecncets = tcpCon.getECNInIP(flag=tm.ECN_CE, path=tm.PATH_FORWARD)
				ecnceval = [500]*len(ecncets)
			
			ecndata = gp.Data(ecncets,ecnceval, title="ECN_CE")
				
			
		
			if len(rtsts) != 0:
				if len(sacksack) != 0:
				
					rtsdata = gp.Data(rtsts,rtsrts, title="Retransmits")
					sackdata = gp.Data(sacksackts, sacksack, title = "SACKs")
					sackenddata = gp.Data(sackendts, sackend, title = "SACKEnd")
				
					congwinplot.plot(congwindata, rtsdata, sackdata, sackenddata, ecndata)
					#congwinplot.plot(congwindata, rtsdata, sackdata)
				else:
					rtsdata = gp.Data(rtsts,rtsrts, title="Retransmits")
					congwinplot.plot(congwindata, rtsdata, ecndata)
			else:
				congwinplot.plot(congwindata, ecndata)
			
			congwinplot.hardcopy(fn+'.png',terminal = 'png')
			
		
		if showRTT:
			#rttplot
			rttts, rttrtt = tcpCon.getRTT(path = tm.PATH_FORWARD)
			rttplot = gp.Gnuplot()
			rttplot.xlabel("time")
			rttplot.ylabel("Round Trip time")
			rttdata = gp.Data(rttts[:drop],rttrtt[:drop], with_="lines")
			rttplot.plot(rttdata)
			
			rttplot.hardcopy('rtt_'+fn+'.png',terminal = 'png')
		
		if showRTTTS:
			#rtttsplot by timestamps
			rtttsts, rtttsrtt = tcpCon.getRTTbyTS(path = tm.PATH_FORWARD)
			rtttsplot = gp.Gnuplot()
			rtttsplot.xlabel("time")
			rtttsplot.ylabel("Round Trip time by TS")
			rtttsdata = gp.Data(rtttsts[:drop],rtttsrtt[:drop], with_="lines")
			rtttsplot.plot(rtttsdata)
			
			rtttsplot.hardcopy('rtts_'+fn+'.png',terminal = 'png')
		
		if showDataTX:
			#Datarate
			drts, drdr = tcpCon.workRate(limit = 40000000, window=200)
			drplot = gp.Gnuplot()
			drplot.xlabel("time")
			drplot.ylabel("Datarate")
			drdata = gp.Data(drts[:drop], drdr[:drop], with_="lines")
			drplot.plot(drdata) 
			drplot.hardcopy('data_'+fn+'.png',terminal = 'png')
		
		
		
		r = raw_input("enter to quit")
	
	
		
		
		
