import socket
import sys
import NSPack
import time


def recvPayload(s, seq=None):
	d = s.recv(2048)
	nsp = NSPack.NSPack(d)
	if nsp.hasPayload():
		print "Got payload, seq", nsp.seqn, ""
		return nsp.seqn
	else:
		print "Did not get payload"
		sys.exit(-1)

def sendAck(s, ackn):
	nsp = NSPack.NSPack()
	nsp.ackn = ackn
	nsp.create()
	d = s.send(nsp.header)
	print "Sent Ack of 1000"
	


port = int(sys.argv[1])
ip = "127.0.0.1"

soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

soc.connect((ip, port))

print "Send SYN"
nsp = NSPack.NSPack()
nsp.synf = True
nsp.create()
soc.send(nsp.header)

time.sleep(1)
d = soc.recv(2048)
nspr = NSPack.NSPack(d)

if not nspr.justSynAck():
	print "Invalid handshake"
	sys.exit()
	
print "got synack, replying with ack"

nsp.synf = False
nsp.ackf = True
nsp.create()
soc.send(nsp.header)
time.sleep(1)
ackn = recvPayload(soc)
time.sleep(1) 
sendAck(soc, ackn)

ackna = recvPayload(soc)
acknb = recvPayload(soc)
time.sleep(1)
sendAck(soc, ackna)
sendAck(soc, acknb)

ackna = recvPayload(soc)
acknb = recvPayload(soc)
acknc = recvPayload(soc)
time.sleep(1)
sendAck(soc, ackna)
sendAck(soc, acknb)
sendAck(soc, acknc)
