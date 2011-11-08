import struct
import datetime



#Link types
LL_ETHERNET = 1
LL_IEEE802_11 = 105

class PcapPacket(object):
	
	def __init__(self, data="", reversed=False):
		self.data = data
		self.reversed = reversed
		self.time = None #datetime.time(hours, mins, seconds, uSecs)
		self.pLen = None #Packet length on file
		self.oLen = None #Original Length
		self.sec = None
		self.uSec = None
		self.pData = None
	
		if not self.reversed:
			self.sec , self.uSec, self.pLen, self.oLen = struct.unpack("<IIII", data[0:16])
		else:
			self.sec , self.uSec, self.pLen, self.oLen = struct.unpack("<IIII", data[0:16])
		
		
		self.time = datetime.datetime.fromtimestamp(self.sec+self.uSec/1000000.)
		
		
		#Format the time....
		#minutes = self.sec/60
		#hours = minutes/60
		#minutes = minutes%60
		#seconds = self.sec%60
		#print self.sec, self.uSec, hours, minutes, seconds, self.uSec
		#self.time = datetime.time(hours, minutes, seconds, self.uSec)
			
	def addPacketData(self, data):
		"""
		Add all the packet data in the packet?
		"""
		
		self.pData = data


class PcapRead(object):

	def __init__(self):
		
		self.reversed = None
		self.f = None
		self.binGHeader = None
		self.magicNumber = None
		self.versionNumberMajor = None
		self.versionNumberMinor = None
		self.tsSigFigs = None
		self.snapLen = None
		self.netType = None
		
	def open(self, path):
		"""
		this will open a file... Will raise exceptions for a normal file that will
		have to be caught!
		"""
		
		self.f = open(path, "r")
		gHead = self.f.read(24) #header is 24 bytes!
		
		self.magicNumber = gHead[:4]
		
		if self.magicNumber != "\xA1\xB2\xC3\xD4":
			if self.magicNumber != "\xD4\xC3\xB2\xA1":
				return False
			else:
				print "Reversed"
				self.reversed = True
		else:
			self.reversed = False
		
		if not self.reversed:
		
			self.versionNumberMajor , self.versionNumberMinor = struct.unpack(">HH", gHead[4:8])
			self.tsSigFig, self.snapLen, self.netType = struct.unpack(">III", gHead[12:24])
		else:
			self.versionNumberMajor , self.versionNumberMinor = struct.unpack("<HH", gHead[4:8])
			self.tsSigFig, self.snapLen, self.netType = struct.unpack("<III", gHead[12:24])
		
		return True
	
	def nextPack(self):
		"""
		This will read the next packet!
		"""
		#Grab the header
		hData = self.f.read(16)
		if len(hData) < 16:
			return False
		p = PcapPacket(data=hData, reversed=self.reversed)
		pData = self.f.read(p.pLen)
		
		p.addPacketData(pData)
		
		return p
		
			
		
