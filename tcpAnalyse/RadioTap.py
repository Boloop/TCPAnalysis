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
}



class RadioTap(object):
	"""
	"""
	
	def __init__(self, data):
		self.data = data
		
		ver, pad, length = struct.unpack("BBH", data[0:4])
		self.ver = ver
		self.pad = pad 
		self.length = length
		
		
		#Load up all the flags!
		self.flags = []
		
		i = 0
		while True:
			flags = struct.unpack("<I", data[4+i:8+i])[0]
			self.flags.append(flags)
			print i, flags
			print "%6x" % (flags)
			if not flags & 0x80:
				break
			i += 1
	
	
	
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
				result += str(x)+", "
			else:
				result += FLAGTONAME[x]+", "
		
		return result
			
			
