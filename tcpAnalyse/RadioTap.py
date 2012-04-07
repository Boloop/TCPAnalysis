"""
This will handle all the data in a radioTap format
"""

import struct

FLAG_TSFT = 0 #Time Sycrnoise Function timer? u64 MacTime
FLAG_FLAGS = 1 #More flags? :o u8
FLAG_RATE = 2 #TX Rate 500Kbps u8
FLAG_CHANNEL = 3 #Channel u16 Freq, u16 Flags
FLAG_FHSS = 4 #Frequency Hopping u8 hopset u8 hop Pattern
FLAG_ANTENNA_SIGNAL = 5 #Power being recieved in dBm s8!
FLAG_ANTENNA_NOISE = 6 #Noise being received in dBm s8!
FLAG_LOCK_QUALITY = 7 #Some Arb Sig Qual? u16
FLAG_TX_ATTENUATION = 8 # Tx Power? u16
FLAG_DB_TX_ATTENUATION = 9# TX power? u16
FLAG_DB_TX_POWER = 10 # tx power s8
FLAG_ANTENNA_INDEX = 11 # Which antenna it came from?
FLAG_DB_ANTENNA_SIGNAL = 12 #RF Signal power at antenna u8
FLAG_DB_ANTENNA_NOISE = 13 #RF Signal noise at antenna u8
FLAG_RX_FLAGS = 14 #Some RX flags! :o u16
FLAG_MCS = 19 #Some 802.11n rate? u8 known, u8 flags u8 mcs
FLAG_UNKNOWN15 = 15
FLAG_UNKNOWN17 = 17


FLAGTODATALENGTH = {
 FLAG_TSFT:64,
 FLAG_FLAGS:8,
 FLAG_RATE:8,
 FLAG_CHANNEL:32,
 FLAG_FHSS:8,
 FLAG_ANTENNA_SIGNAL:8,
 FLAG_ANTENNA_NOISE:8,
 FLAG_LOCK_QUALITY:16,
 FLAG_TX_ATTENUATION: 16,
 FLAG_DB_TX_ATTENUATION:16,
 FLAG_DB_TX_POWER: 8,
 FLAG_ANTENNA_INDEX: 8,
 FLAG_DB_ANTENNA_SIGNAL: 8,
 FLAG_DB_ANTENNA_NOISE: 8,
 FLAG_RX_FLAGS: 16,
 FLAG_MCS: 24, 
 
 FLAG_UNKNOWN15:16,
 FLAG_UNKNOWN17:16,
}



FLAGTONAME = {
 FLAG_TSFT:"TSFT/MacTime",
 FLAG_FLAGS:"Flags-1",
 FLAG_RATE:"Rate",
 FLAG_CHANNEL:"Channel",
 FLAG_FHSS:"Freq Hoppin",
 FLAG_ANTENNA_SIGNAL:"Antenna Signal",
 FLAG_ANTENNA_NOISE:"Antenna Noise",
 FLAG_LOCK_QUALITY:"Lock/Signal Quality",
 FLAG_TX_ATTENUATION: "TX Attentuation",
 FLAG_DB_TX_ATTENUATION:"TX db Attenuataion",
 FLAG_DB_TX_POWER: "TX power",
 FLAG_ANTENNA_INDEX: "Attenna Index",
 FLAG_DB_ANTENNA_SIGNAL: "db Antenna Signal",
 FLAG_DB_ANTENNA_NOISE: "db Antenna Noise",
 FLAG_RX_FLAGS: "RX flags",
 FLAG_MCS: "MCS",
 FLAG_UNKNOWN15: "Guessed 15",
 FLAG_UNKNOWN17: "Guessed 17",
}

HEADERSIZE = 64

TYPE_MANAGEMENT = 0
TYPE_CONTROL = 1
TYPE_DATA = 2
TYPE_RESERVED = 3

TYPETONAME = {
 TYPE_MANAGEMENT:"Management",
 TYPE_CONTROL:"Control",
 TYPE_DATA:"Data",
 TYPE_RESERVED:"Reserved",
 None:"None"
}

SUBTYPE_CONTROL_PS_POLL = 10
SUBTYPE_CONTROL_RTS = 11
SUBTYPE_CONTROL_CTS = 12
SUBTYPE_CONTROL_ACK = 13
SUBTYPE_CONTROL_CFEND = 14
SUBTYPE_CONTROL_CFEND_CF_ACK = 15

SUBTYPECONTROLTONAME = {
 SUBTYPE_CONTROL_PS_POLL:"PS POLL",
 SUBTYPE_CONTROL_RTS: "RTS",
 SUBTYPE_CONTROL_CTS: "CTS",
 SUBTYPE_CONTROL_ACK: "ACK",
 SUBTYPE_CONTROL_CFEND: "CFEnd",
 SUBTYPE_CONTROL_CFEND_CF_ACK: "CFEnd CF-ACK",
}


def binToHex(data):
	result = ""
	for c in data:
		result += "{0:02x}".format(ord(c))
	
	return result


def decodeTSFT(data):
	"""
	This will read the binary of TSFT and return the int of the mactimestamp
	"""
	return struct.unpack("<Q", data)[0]
	
def decodeFlags(data):
	"""
	Will read  FLAG_FLAGS
	"""
	return struct.unpack("B", data)[0]

def decodeRate(data):
	"""
	Will return speed in kbps!
	"""
	return struct.unpack("B", data)[0]*500

def decodeChannel(data):
	"""
	will return freq in Mhz and flags
	"""
	
	freq, flags = struct.unpack("<HH", data)
	
	return (freq, flags)

def decodeAntennaSignal(data):
	"""
	Will Signal in dBm
	"""
	return struct.unpack("b", data)[0]


def decodeAntennaIndex(data):
	"""
	Will Signal in dBm
	"""
	return struct.unpack("B", data)[0]

def decodeRXFlags(data):
	"""
	Will read FLAG_RX_FLAGS
	"""

	return struct.unpack("<H", data)[0]
	
class RadioTap(object):
	"""
	"""
	
	def __init__(self, data):
	
	
	
		self.data = data
		self.header = None
		
		#Frame Control 2 byte flags/vals
		self.protVer = None
		self.type = None
		self.subtype = None
		self.toDS = None
		self.fromDS = None
		self.moreFlag = None
		self.retry = None
		self.pwrMgr = None
		self.moreData = None
		self.wep = None
		self.order = None
		
		#Other PDU header
		self.duration = None
		self.add1 = None
		self.add2 = None
		self.add3 = None
		self.seqCtrl = None
		self.add4 = None
		
		
		#Inital RadioTap header
		ver, pad, length = struct.unpack("BBH", data[0:4])
		self.ver = ver
		self.pad = pad 
		self.length = length
		
		
		#Load up all the flags for RadioTap header.
		self.flags = []
		
		i = 0
		while True:
			flags = struct.unpack("<I", data[4+i:8+i])[0]
			self.flags.append(flags)
			#print i, flags
			#print "%6x" % (flags)
			if not flags & 0x80:
				break
			i += 1
		
		
		offset = self.getPseudoPLCPLength()
		#print "oOffset", offset, self.getFlagList(), len(self.flags)
		if offset != None:
			#Total offset so we have self.data[toffset:]
			toffset = 4+len(self.flags)*4+(offset/8)
			#print "offset", offset, toffset, len(self.flags)
			self.header = self.data[toffset:toffset+30]
		
		if self.header != None:
		
			#Do the Frame Control flags first
			framectrl = self.header[0:2]
			framectrl = [ord(framectrl[0]), ord(framectrl[1])] #Yeah, need to go from string to int 
									   #for the following code to work :(
			
			#Awful "hack" or misunderstanding...
			fnibble = (framectrl[0] & 0xF0) >> 4
			lnibble = (framectrl[0] & 0x0F)
			lnibble = lnibble >> 2 + ( (lnibble & 0x03) << 2 )
			framectrl[0] = fnibble + (lnibble << 4) 
			
			#print "ok", len(self.header), len(framectrl)
			self.protVer =   ( framectrl[0] & 0xC0) >> 6
			self.type =      ( framectrl[0] & 0x30) >> 4
			self.subtype =   ( framectrl[0] & 0x0F)
			self.toDS =      ( framectrl[1] & 0x80) >> 7
			self.fromDS =    ( framectrl[1] & 0x40) >> 6
			self.moreFlag =  ( framectrl[1] & 0x20) >> 5
			self.retry =     ( framectrl[1] & 0x10) >> 4
			self.pwrMgr =    ( framectrl[1] & 0x08) >> 3
			self.moreData =  ( framectrl[1] & 0x04) >> 2
			self.wep = 	 ( framectrl[1] & 0x02) >> 1
			self.order =     ( framectrl[1] & 0x01)
			
			#Get those addresses, lenghts and stuffs?
			self.duration = struct.unpack("H", self.header[2:4])[0]
			self.add1 = self.header[4:10]
			#print "Human Flags:", self.humanFlags(), self.type, self.subtype
			#print "Header:", binToHex(self.header)
			#print self.humanAddresses()
			#print "Header:", binToHex(frame)
			#print self.humanType()
			
			#This could do with a little cleaning up
			if self.type == TYPE_CONTROL and self.subtype == SUBTYPE_CONTROL_ACK:
				pass
			elif self.type == TYPE_CONTROL and self.subtype == SUBTYPE_CONTROL_RTS:
				self.add2 = self.header[10:16]
				pass
			elif self.type == TYPE_CONTROL and self.subtype == SUBTYPE_CONTROL_CTS:
				self.add2 = self.header[10:16]
				pass
				
			else:
				self.add2 = self.header[10:16]
				self.add3 = self.header[16:22]
				self.seqCtrl = struct.unpack("H", self.header[22:24])[0]
				self.add4 = self.header[24:30]
			
			
	
	
	def getFlagBit(self, x):
		"""
		This will return True/False for what the bit is set in that flag
		"""
		
		
		index = x/32
		mask = 2**( x - index*32 ) 
		
		#print x, index, mask
		
		#Check if the bit is valid!
		if index >= len(self.flags):
			return None
		
		if mask == 0x80:
			return None
		
		return bool( self.flags[index] & mask )
	
	def getFlagList(self):
		"""
		This will return a list of numbers of where flags are set
		"""
		result = []
		
		for i in xrange(len(self.flags)*32):
			 r = self.getFlagBit(i)
			 #print i, r
			 if r == None:
			 	continue
			 if r:
			 	result.append(i)
		return result
	
	def humanFlags(self):
		fl = self.getFlagList()
		
		print fl
		if len(fl) == 0:
			return "None"
		
		result = ""
		
		for x in fl:
			if not x in FLAGTONAME.keys():
				result += "Unknown: "+str(x)+", "
			else:
				result += FLAGTONAME[x]+", "
		
		return result
	
	def humanType(self):
		"""
		Will return human readable string of type and subtype
		"""
		
		result = TYPETONAME[self.type]+" : "
		
		try:
			if self.type == TYPE_CONTROL:
				result += SUBTYPECONTROLTONAME[self.subtype]
		except KeyError:
			result += "Unknown "+str(self.subtype)
		
		return result
	
	def humanAddresses(self):
		"""
		Will return human readable string of all addresses
		"""
		
		result = ""
		
		if self.add1 != None:
			result += " Ad1: "+ binToHex(self.add1)
		if self.add2 != None:
			result += " Ad2: "+ binToHex(self.add2)
		if self.add3 != None:
			result += " Ad3: "+ binToHex(self.add3)
		if self.add4 != None:
			result += " Ad4: "+ binToHex(self.add4)
		
		return result
	def getPseudoPLCPLength(self):
		"""
		Funny function name for working out the sizes of all the flagged feilds
		Will return None if cannot work out due to unknown feild length
		"""
		
		result = 0
		fl = self.getFlagList()
		for f in fl:
			if not f in FLAGTODATALENGTH.keys():
				return None
			
			result += FLAGTODATALENGTH[f]
		
		return result
	
	def containsAddress(self, add):
		"""
		Will return a boolean if any address equals one given
		"""
		
		if self.add1 == add:
			return True
		if self.add2 == add:
			return True
		if self.add3 == add:
			return True
		if self.add4 == add:
			return True
		
		return False
	
	def readFlag(self, flag):
		"""
		Will fetch and decode that flag type.
		"""
		
		fl = self.getFlagList()
		
		if not flag in fl:
			return None
		
		offset = 0
		for f in fl:
			if f != flag:
				offset += FLAGTODATALENGTH[f]
				continue
			else:
				#got the offset
				break
		
		offset += HEADERSIZE
		byte = offset/8
		endbyte = FLAGTODATALENGTH[flag]/8 + byte
		data = self.data[byte:endbyte]
		
		
		if flag == FLAG_TSFT:
			return decodeTSFT(data)
			
		if flag == FLAG_FLAGS:
			return decodeFlags(data)
		
		if flag == FLAG_RATE:
			return decodeRate(data)
		
		if flag == FLAG_CHANNEL:
			return decodeChannel(data)
		
		if flag == FLAG_ANTENNA_SIGNAL:
			return decodeAntennaSignal(data)
		
		if flag == FLAG_ANTENNA_INDEX:
			return decodeAntennaIndex(data)
		
		if flag == FLAG_RX_FLAGS:
			return decodeRXFlags(data)
		
		
		
		return None
			
				
			
			
