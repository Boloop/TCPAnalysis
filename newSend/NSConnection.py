#
#
#

import NSPack
import random

STATE_NONE = 0
STATE_SYNACK = 1
STATE_CONNECTED = 2

class NSConnection(object):

	def __init__(self):
		pass
		self.connid = None
		self.dip = None
		self.dport = None
		self.sip = None
		self.state = STATE_NONE
		self.sendsoc = None
		self.ipport = None
		
	
	def genSyn(self):
		"""
		If we're making the connection, I say!
		"""
		self.connid = random.randint(0, 2**32-1)
		
	
	def fromSyn(self, nspack, ipport):
		"""
		Just got a syn packet, create a new socket. 
		"""
		self.state = STATE_SYNACK
		self.connid = nspack.connid
		self.dip = ipport[0]
		self.dport = ipport[1]
		
	def ackSyn(self):
		"""
		This will create a SynAck packet to reply
		"""
		nsp = NSPack.NSPack()
		nsp.synf = True
		nsp.ackf = True
		nsp.create()
		
		self.sendsoc(nsp.header, (self.dip, self.dport))
		
	#def sendSynAck(self):
			
	def ourpack(self, nspack, ipport):
		return self.dip == ipport[0] and nspack.connid == self.connid and self.dport == ipport[1]
	
	def recvPack(self, nspack, ts):
		
		if nspack.justSyn():
			print "RecvPack, Just Syn"
			if self.state == STATE_SYNACK:
				#Reply with a SYNACK again
				print "State is synack, resending synack"
				self.ackSyn()
			else:
				print "Just Just Syn with a connection already made..."
				return
		
		
		if nspack.justSynAck():
			self.state = STATE_CONNECTED
			nsp = NSPack.NSPack()
			nsp.connid = nspack.connid
			nsp.ackf = True
			nsp.create()
			self.sendsoc(nsp.header, nspack.ipport)
			
