# This module will lay out and read in NSPack packets
#

import struct

class NSPack(object):

	def __init__(self, data=None):
		
		self.synf = False
		self.ackf = False
		self.connid = 0
		
		self.seqn = 0
		self.ackn = 0
		self.recv = 0
		
		self.data = None
		self.header = None
		self.valid = False
		
		self.ipport = None
		
		self.payload = ""
		
		if data:
			self.valid = self.readData(data)
		
	def readData(self, data):
		self.data = data
		try:
			self.connid, flagbyte, self.seqn, self.ackn, self.recv = struct.unpack(">IBIII", data[0:17])
		
			self.synf = bool( flagbyte & 1 )
			self.ackf = bool( flagbyte & 2 )
			
			self.payload = data[17:]
		except:
			return False
		return True
	
	def hasPayload(self):
		return len(self.payload) != 0
	
	def justSyn(self):
		"""
		Will return boolean if this is just a syn for a new connection
		"""
		
		return self.synf and not self.ackf
		
	def justSynAck(self):
		return self.synf and self.ackf
		
	def create(self):
		"""
		Will create packet from setup flags into a binary
		string
		"""
		
		flagbyte = 0
		if self.synf: flagbyte += 1
		if self.ackf: flagbyte += 2
		
		self.header = struct.pack(">IBIII", self.connid, flagbyte, self.seqn, self.ackn, self.recv)
		
		self.data = self.header+self.payload

