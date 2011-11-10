import PcapReader as pcr
import TcpMon as tm
import sys
import Gnuplot as gp
import dpkt
import struct

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
	
	
	print "File Loaded"
	
	
	syn, synack, ack = tcpCon.getHandshake()
	syno = tm.TCPOptions( syn[1].opts )
	synacko = tm.TCPOptions( synack[1].opts )
	acko = tm.TCPOptions( ack[1].opts )
	print syn[0], syno
	print synack[0], synacko
	print ack[0], acko	
	
	
						   
