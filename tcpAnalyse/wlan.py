"""
Presently, a demo app that will open up pcap RadioTap Link Layer captures!
"""



import PcapReader as pcr
import TcpMon as tm
import sys
import Gnuplot as gp
import dpkt
import struct

import RadioTap as rt

if __name__ == "__main__":

	if len(sys.argv) < 2:
		print "Please ensure you have got [path]"
		sys.exit()

	path = sys.argv[-1]
	
	p = pcr.PcapRead()
	if not p.open(path):
		print "whoops?"
		#print ("Incorrect header. :( magic number was {:x}".format(p.magicNumber))
	
	print "Pcap file open details:"
	print "R: {0} V:{1}.{2} NetType: {3}".format( p.reversed, p.versionNumberMajor, p.versionNumberMinor, p.netType) 
	
	if p.netType != pcr.LL_IEEE802_11_RADIO:
		print "Does not support this Link Type :( QUITTING"
		sys.exit() 
	
	while 1:
		packet = p.nextPack()
		if not packet:
			print "EOF"
			break
		
		pkt = packet.pData
		rframe = rt.RadioTap(pkt)
		
		print rframe.humanFlags()
		print len(pkt)
