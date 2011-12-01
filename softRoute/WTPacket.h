/*
 * WTPacket.h
 *
 *  What The Packet!? Reads Ethernet Frames :)
 *
 *  This will try and figure out what a frame consists of (SRC/DST mac and what Ether type)
 *  and try and work with ipv4!
 */

#ifndef WTPACKET_H_
#define WTPACKET_H_

#include <stdio.h>
#include <stdlib.h>

class WTPacket {

public:
	char* m_pFrame;
	int m_nFrameLength;


	bool m_bIPv4;
	unsigned char* m_pIPAddrDst;
	unsigned char* m_pIPAddrSrc;
	char* m_pMacDst;
	char* m_pMacSrc;



public:
	WTPacket(char*, int);
	bool process();
	virtual ~WTPacket();
};

#endif /* WTPACKET_H_ */
