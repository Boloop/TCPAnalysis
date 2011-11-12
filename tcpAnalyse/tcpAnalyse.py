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
	path = sys.argv[1]
	
	p = pcr.PcapRead()
	if not p.open(path):
		print "whoops?"
		#print ("Incorrect header. :( magic number was {:x}".format(p.magicNumber))
	
	print "Pcap file open details:"
	print "R: {0} V:{1}.{2} NetType: {3}".format( p.reversed, p.versionNumberMajor, p.versionNumberMinor, p.netType) 
	
	if p.netType != pcr.LL_ETHERNET and p.netType != pcr.LL_LINUX_SLL:
		print "Does not support this Link Type :( QUITTING"
		sys.exit() 
	
	
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
					tcpCon.addPacket(ip.data, packet.time)
					#print "Yay"
				else:
					print "Nay"
			
					
				
		
		
		#print packet.time, packet.pLen
	
	print "File loaded"
	
	if tcpCon:
		ipa = strIP(tcpCon.ip1)+":"+str(tcpCon.port1)
		ipb = strIP(tcpCon.ip2)+":"+str(tcpCon.port2)
		print ipa+" >>  FORWARD  >> "+ipb
		print ipa+" <<  BACKWARD << "+ipb
		
		
		#Congestion Window
		wints, winwin = tcpCon.unackdPackets()
		congwinplot = gp.Gnuplot()
		congwinplot.xlabel("time")
		congwinplot.ylabel("Congestion Window size")
		congwindata = gp.Data(wints[:-3],winwin[:-3], with_="filledcurves", title="Congestion Window")
		
		rtsts, rtsrts, l = tcpCon.getRetransmits()
		
		if len(rtsts) != 0:
			rtsdata = gp.Data(rtsts,rtsrts, title="Retransmits")
			congwinplot.plot(congwindata, rtsdata)
		else:
			congwinplot.plot(congwindata)
			
		
	
		#rttplot
		rttts, rttrtt = tcpCon.getRTT(path = tm.PATH_FORWARD)
		rttplot = gp.Gnuplot()
		rttplot.xlabel("time")
		rttplot.ylabel("Round Trip time")
		rttdata = gp.Data(rttts[:-3],rttrtt[:-3], with_="lines")
		rttplot.plot(rttdata)
		
		#Datarate
		drts, drdr = tcpCon.workRate(limit = 40000000, window=200)
		drplot = gp.Gnuplot()
		drplot.xlabel("time")
		drplot.ylabel("Datarate")
		drdata = gp.Data(drts[:-3], drdr[:-3], with_="lines")
		drplot.plot(drdata) 
		
		
		
		r = raw_input("enter to quit")
	
	
		
		
		
