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
	m_pArpTable = NULL;


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

void InterfaceOutput::setArpTable(ArpTable* tbl)
{
	/*
	 * this will load a static Arp Table
	 */

	m_pArpTable = tbl;
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


	WTPacket pack((char*)data, len);
	bool processed = pack.process();


	if(m_bPrintPackets)
	{
		if (len >= 12)
		{

			if(!processed)
			{
				printf("OUTPUTTUNG %s Did not understand packet\n", m_sInterface);
			}
			else
			{
				if (!pack.m_bIPv4)
				{
					printf("OUTPUTTUNG %s Des: %02X:%02X:%02X:%02X:%02X:%02X Src %02X:%02X:%02X:%02X:%02X:%02X\n",
										m_sInterface, data[0], data[1], data[2], data[3], data[4] ,data[5] ,data[6] ,data[7] ,
										data[8], data[9], data[10], data[11]);
				}
				else
				{
					printf("OUTPUTTUNG %s Des: %d.%d.%d.%d Src:  %d.%d.%d.%d\n", m_sInterface,
							pack.m_pIPAddrDst[0], pack.m_pIPAddrDst[1], pack.m_pIPAddrDst[2], pack.m_pIPAddrDst[3],
							pack.m_pIPAddrSrc[0], pack.m_pIPAddrSrc[1], pack.m_pIPAddrSrc[2], pack.m_pIPAddrSrc[3]);


				}
			}

		}
		else
		{
			printf("OUTPUTTUNG %s, Bloody Tiny frame!?", m_sInterface);
		}

	}

	if (processed && m_pArpTable != NULL)
	{
		if(pack.m_bIPv4){

			//Find that mac address!
			char* dstmac = m_pArpTable->findMacFromIP((char*)pack.m_pIPAddrDst);
			if(dstmac == NULL)
			{
				printf("IP not in file?\n");
			}
			else
			{
				printf("Found Mac, copying it across!\n");
				memcpy((void*)data, (void*)dstmac, 6);
			}//if found mac

		}// if ipv4
	}// if got table and processed frame

	pcap_inject(m_pDev, (void*)data, len);
}

InterfaceOutput::~InterfaceOutput() {
	// TODO Auto-generated destructor stub

	free(m_sErrBuf);
}
