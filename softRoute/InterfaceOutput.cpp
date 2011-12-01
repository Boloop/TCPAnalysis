/*
 * InterfaceOutput.cpp
 *
 *  Created on: 26 Nov 2011
 *      Author: one
 */


#include "InterfaceOutput.h"

InterfaceOutput::InterfaceOutput(char* interface) {
	// TODO Auto-generated constructor stub


	m_sErrBuf = (char*)malloc(PCAP_ERRBUF_SIZE);
	m_pDev = NULL;
	m_sInterface = interface;
	m_bInjectWithBroadcast = false;
	m_bPrintPackets = false;


}
bool InterfaceOutput::open()
{
	/*
	 * This will open up the pcap interface, boolean if successful or not
	 * true = :) , false = :(
	 */


	m_pDev = pcap_open_live(m_sInterface, BUFSIZ, 1, 1000, m_sErrBuf);
	if(m_pDev == NULL)
	{
		fprintf(stderr, "Unable to open device: %s for injection: %s\n", m_sInterface, m_sErrBuf);
		return false;
	}
	return true;

}

void InterfaceOutput::usePcap(pcap_t* pcap)
{
	/*
	 * Will be given an ALREADY OPEN pcap_t handler
	 */

	m_pDev = pcap;

}

void InterfaceOutput::setBroadcast(bool val)
{
	/*
	 * Append FF:FF:FF:FF:FF:FF to destination address on all injections?
	 */

	m_bInjectWithBroadcast = val;
}

void InterfaceOutput::setPrintPackets(bool val)
{
	/*
	 * Will print summary of packets when inject
	 */
	m_bPrintPackets = val;
}

void InterfaceOutput::inject(u_char* data, int len)
{
	/*
	 * Will inject the data! :D
	 */
	if(m_bInjectWithBroadcast)
	{
		memset(data, 0xFF, 6);
	}

	if(m_bPrintPackets)
	{
		if (len >= 12)
		{
			printf("OUTPUTTUNG %s Des: %02X:%02X:%02X:%02X:%02X:%02X Src %02X:%02X:%02X:%02X:%02X:%02X\n",
					m_sInterface, data[0], data[1], data[2], data[3], data[4] ,data[5] ,data[6] ,data[7] ,
					data[8], data[9], data[10], data[11]);
		}
		else
		{
			printf("OUTPUTTUNG %s, Bloody Tiny frame!?", m_sInterface);
		}

	}
	pcap_inject(m_pDev, (void*)data, len);
}

InterfaceOutput::~InterfaceOutput() {
	// TODO Auto-generated destructor stub

	free(m_sErrBuf);
}
