/*
 * WTPacket.cpp
 *
 *  See WTPacket.h for general comment details! :D
 */

#include "WTPacket.h"

WTPacket::WTPacket(char* pFrame, int len) {
	// constructor stub
	m_pFrame = pFrame;
	m_nFrameLength = len;

	m_bIPv4 = false;
	m_pIPAddrDst = NULL;
	m_pIPAddrSrc = NULL;
	m_pMacDst = NULL;
	m_pMacSrc = NULL;

}

bool WTPacket::process()
{
	/*
	 * This will read and process the frame data and find out what it is
	 * return true for success, false for failure
	 */

	if (m_nFrameLength < 14) // No space to read dst/src mac and ether type!
		return false;
	m_pMacDst = m_pFrame;
	m_pMacSrc = m_pFrame+6;

	if(m_pFrame[6] == 0x80 && m_pFrame[7] == 0x00)
	{
		m_bIPv4 = true;
	}

	if(!m_bIPv4) // Code only process ipv4 addresses :(
		return true;

	if(m_nFrameLength < 34) // 14+ 20 ipv4 header!
		return false;

	m_pIPAddrSrc = m_pFrame+26;
	m_pIPAddrSrc = m_pFrame+30;

	return true;



}

WTPacket::~WTPacket() {
	// destructor stub
}
