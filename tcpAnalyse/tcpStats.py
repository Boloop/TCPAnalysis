"""
Will perform TCP stats upon a file(s)
"""

import sys
import TcpMon as tm
import UdpMon as um
import PcapReader
import dpkt
import struct

def strIP(ipadd):
	"""
	Will convert to binary to spit out an int of the address
	"""
	a,b,c,d = struct.unpack("BBBB", ipadd)
	return str(a)+"."+str(b)+"."+str(c)+"."+str(d)
	
	
def loadPcap(path):
	"""
	"""
	p = PcapReader.PcapRead()
	if not p.open(path):
		print "whoops?"
		#print ("Incorrect header. :( magic number was {:x}".format(p.magicNumber))
		
	
	
	print "Pcap file open details:"
	print "R: {0} V:{1}.{2} NetType: {3}".format( p.reversed, p.versionNumberMajor, p.versionNumberMinor, p.netType) 
	
	if p.netType != PcapReader.LL_ETHERNET and p.netType != PcapReader.LL_LINUX_SLL:
		print "Does not support this Link Type :( QUITTING"
		sys.exit() 
	
	tcpCon = None
	udpCon = None
	
	
	
	while 1:
		packet = p.nextPack()
		if not packet:
			print "EOF"
			break
		
			
			
		#Lets find out what it's made of!
		if   p.netType == PcapReader.LL_ETHERNET:
			eth = dpkt.ethernet.Ethernet(packet.pData)
		elif p.netType == PcapReader.LL_LINUX_SLL:
			eth = dpkt.ethernet.Ethernet(packet.pData[2:]) # Hacks, lol. Just don't try to read the ethernet 
								       # frame. Addys wrong, but ethertype right!
								       # http://www.tcpdump.org/linktypes/LINKTYPE_LINUX_SLL.html
		
		#Is it an IP packet, yeah?
		if type(eth.data) == type(dpkt.ip.IP()) and udpCon == None:
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
					print "Nay-TCP"
			
		if type(eth.data) == type(dpkt.ip.IP()) and tcpCon == None:
			#It is, It is an ip packet!
			ip = eth.data
			#print "is it UDP?"
			if type(ip.data) == type(dpkt.udp.UDP()):
				#it's UDP
				#Lock And load
				if udpCon == None:
					udpCon = um.UdpCon(ip, packet.time)
					
				elif udpCon.sameSocket(ip):
					udpCon.addIPPacket(ip, packet.time)
					#tcpCon.addPacket(ip.data, packet.time)
					#print "Yay"
				else:
					print "Nay-UDP"
		
		
		#print packet.time, packet.pLen
	
	print "File loaded"
	if udpCon != None:
		print "contains UDP connection"
		#Cheeky
		tcpCon = udpCon
	elif tcpCon != None:
		print "contains TCP Connection"
	
	return tcpCon

def getAvg(data):
	"""
	Will work out average of the data
	(time, value)
	"""
	times , values = data 
	
	if len(times) != len(values):
		return None
	
	if len(times) == 1:
		return values[0]
	
	accum = 0
	index = 1
	while index < len(times):
		tdif = times[index] - times[index-1]
		
		area = 0.5*tdif*(values[index]+values[index-1])
		accum += area 
		
		index += 1
	
	return accum/(times[-1]-times[0])
		
	



class TcpStat(object):

	def __init__(self, tcpmon):
		
		self.tm = tcpmon
	
		self.congWin = None
		self.avgOverall = None
		self.avgtxRateWindow = None
		self.congWinAvg = None
		self.retransmits = None
		self.countRetransmits = None
		self.retransmitPercent = None
		self.overalDataAmount = None
		self.retransmitDataCount = None
		self.rttTS = None
		self.minRTT = None
		self.maxRTT = None
		self.avgRTT = None
		
		self.tData = None
		self.tTime = None
		
	def getCongWin(self):	
		"""
		Will load up in the congWindow
		"""
		
		if self.congWin == None:
			self.congWin = self.tm.unackdPackets()
		
		return self.congWin
	
	def getAvgCongWin(self):
		"""
		"""
		
		if self.congWinAvg == None:
			self.congWinAvg = getAvg(self.getCongWin())
		
		return self.congWinAvg
	
	def getRetransmits(self):
		"""
		"""
		if self.retransmits == None:
			self.retransmits = self.tm.getRetransmits()
		return self.retransmits
	
	def getCountRetransmits(self):
		"""
		"""
		if self.countRetransmits == None:
			self.countRetransmits  = len(self.getRetransmits()[0])
		return self.countRetransmits
	
	def getOveralDataAmount(self):
		"""
		"""
		if self.overalDataAmount == None:
			self.overalDataAmount = self.tm.getOveralData()
		
		return self.overalDataAmount
	
	def getRetransmitDataCount(self):
		"""
		"""
		if self.retransmitDataCount == None:
			retrans = self.getRetransmits()
			#Calculate the data that had been retransmitted...
			ts, segmentnumber, lengths = retrans
			accum = 0
			for n in lengths:
				accum += n
			self.retransmitDataCount = accum
			
		return self.retransmitDataCount 
		
	def getRetransmitPercent(self):
		if self.retransmitPercent == None:
			
			
		
			self.retransmitPercent = float(self.getRetransmitDataCount())/float(self.getOveralDataAmount())
			self.retransmitPercent *= 100
		
		return self.retransmitPercent
		
	def getDataStats(self):
		if self.tData == None:
			self.tData, self.tTime = tcpCon.getTXRate()
		return self.tData, self.tTime
	
	def getRTTTS(self):
		if self.rttTS == None:	
			self.rttTS = self.tm.getRTTbyTS()
		return self.rttTS

	
	def getRTTTSstats(self):
		if self.avgRTT == None:
			times, rtts = self.getRTTTS()
			
			self.minRTT = 0
			total = 0
			for r in rtts:
				total += r
				if self.minRTT == 0:
					self.minRTT = r
					self.maxRTT = r
				if self.minRTT > r:
					self.minRTT = r
				if self.maxRTT < r:
					self.maxRTT = r
			
			self.avgRTT = float(total)/len(rtts)
		
		return self.minRTT, self.maxRTT, self.avgRTT
	
	def getDic(self):
		"""
		Will return a dictionary summery of results
		"""
		result = {}
		
		result["CONGavg"] = self.getAvgCongWin()
		result["RETRANScount"] = self.getRetransmitDataCount()
		result["RETRANSdata"] = self.getOveralDataAmount()
		result["RETRANSpercent"] = self.getRetransmitPercent()
		rttmin, rttmax, rttavg = self.getRTTTSstats()
		result["RTTmin"] = rttmin
		result["RTTmax"] = rttmax
		result["RTTavg"] = rttavg
		result["DATAoverall"] = self.getOveralDataAmount()
		result["DATAtotal"], result["TIME"] = self.getDataStats()
		
		return result
		
				 
	
if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		print "no path?"
		sys.exit(-1)
	
	tcpCon = loadPcap(sys.argv[1])
	
	tcpCon.setOrigin()
	tcpCon.removeFIN()
	tcpstat = TcpStat(tcpCon)
	
	#Print stats
	ipa = strIP(tcpCon.ip1)+":"+str(tcpCon.port1)
	ipb = strIP(tcpCon.ip2)+":"+str(tcpCon.port2)
	print ipa+" >>  FORWARD  >> "+ipb+" ["+str(len(tcpCon.forward))+"]["+str(len(tcpCon.forwardECN))+"]"
	print ipa+" <<  BACKWARD << "+ipb+" ["+str(len(tcpCon.backward))+"]["+str(len(tcpCon.backwardECN))+"]" 
	count = tcpCon.getPacketCount()
	print "Contains",count,"packets"
	wrData = tcpCon.workRate(window=2)
	wrAvg = getAvg(wrData)
	
	tdata, tdif = tcpCon.getTXRate()
	
	avgcongwin = tcpstat.getAvgCongWin()
	retransmitcount = tcpstat.getCountRetransmits()
	retransmitpercent = tcpstat.getRetransmitPercent()
	rttmin, rttmax, rttavg = tcpstat.getRTTTSstats()
	result = tcpstat.getDic()
	print "wrAvg", wrAvg
	print "{0} bytes sent over {1}secs at {2}bytes/sec".format(tdata, tdif, tdata/tdif)
	print "avg CongWin", avgcongwin
	print "retransmit count", retransmitcount
	print "retransmit percent", retransmitpercent
	print "Rtt min, max, avg", rttmin, rttmax, rttavg
	
	
