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

	m_pBufferQueue = NULL;
	m_bIsDead = false;

	m_nOutputRate = 0;
	m_tvNextPacket.tv_sec = 0;
	m_tvNextPacket.tv_usec = 0;
	m_nDropRate = 0;


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

void InterfaceOutput::setOutputRate(int val)
{
	/*
	 * This will set the output rate of the device in byte/sec
	 */

	m_nOutputRate = val;
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
	bool drop = false;
	timeval tv;




	if (m_nOutputRate != 0)
	{
		/*
		 * See if packet needs dropping, if too soon.
		 */
		gettimeofday(&tv, NULL);
		//printf("time now %d:%d\n", tv.tv_sec, tv.tv_usec);
		if (tv.tv_sec > m_tvNextPacket.tv_sec || ( tv.tv_usec > m_tvNextPacket.tv_usec && tv.tv_sec == m_tvNextPacket.tv_sec ) )
		{
			//Can send, push the timedate back!

			//Work how far to set the fecker back
			int t = (len*1000000)/m_nOutputRate; // time in uSec!
			printf("packet of %d has %duS TX time\n", len, (__suseconds_t)t);

			m_tvNextPacket.tv_usec = tv.tv_usec;
			m_tvNextPacket.tv_sec = tv.tv_sec;

			m_tvNextPacket.tv_usec += (__suseconds_t)t;
			printf("adding %d to %d\n", (__suseconds_t)t, m_tvNextPacket.tv_usec);
			while (m_tvNextPacket.tv_usec >= 1000000)
			{
				m_tvNextPacket.tv_usec -= 1000000;
				m_tvNextPacket.tv_sec += 1;

			}
			//printf("wait for %d:%d\n", m_tvNextPacket.tv_usec, m_tvNextPacket.tv_usec);



		}
		else
		{
			printf("dropped\n");
			drop = true;
		}



	}


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
				//printf("Found Mac, copying it across!\n");
				memcpy((void*)data, (void*)dstmac, 6);
			}//if found mac

		}// if ipv4
	}// if got table and processed frame

	if(drop) return;

	pcap_inject(m_pDev, (void*)data, len);
}

void InterfaceOutput::addInputBuffer(BufferQueue * bq)
{

	m_pBufferQueue = bq;

}

void InterfaceOutput::kill()
{
	/*
	 * This will set the isDead to true, to stop the thread
	 */


	m_bIsDead = true;

}


void InterfaceOutput::Execute()
{
	/*
	 *  This will loop checking the buffer :o	 *
	 */

	if (m_pBufferQueue == NULL)
		return;


	if (m_bPrintPackets) printf("Output Thread Started\n");
	char* buf = (char*)malloc(1500);
	int size, t, p;

	while(1)
	{


		m_pBufferQueue->lock();
		p = -5;
		while( (p = m_pBufferQueue->packetsInQueue() ) == 0)
		{
			// No packets in queue, wait until there is
			if (m_bPrintPackets) printf("Waiting For Data\n");
			if(m_pBufferQueue->waitForData() == 0)
			{
				// there is data, send it!
				break;
			}
			if(m_bIsDead)
					break;
		}
		//There is some packets to get at this point or dead, so check if dead
		if(m_bIsDead)
		{
			m_pBufferQueue->unlock();
			break;
		}

		//Okay, there is a packet, copy it!
		size = m_pBufferQueue->removeFromBottom(buf);

		m_pBufferQueue->unlock();

		if(size == 0)
		{
			printf("Sending Data of zero size? Skipping!\n");
			continue;
		}


		//Free locks, got data, now wait for TX time and inject.

		if (m_bPrintPackets) printf("Sleeping\n");
		if(m_nOutputRate != 0)
		{
			//Work how far to set the fecker back
			t = (size*1000000)/m_nOutputRate; // time in uSec!
			if (m_bPrintPackets) printf("Sleeping for %d\n", t);
			usleep((useconds_t)t);
		}

		//Drop based on dropRate
		bool drop = false;
		if (m_nDropRate != 0)
		{
			int rnd = rand()%1000;
			if(rnd < m_nDropRate)
				drop = true;

		}


		WTPacket pack((char*)buf, size);
		bool processed = pack.process();

		//Get the right MAC
		if (processed && m_pArpTable != NULL)
		{
			if(pack.m_bIPv4){

				//Find that mac address!
				char* dstmac = m_pArpTable->findMacFromIP((char*)pack.m_pIPAddrDst);
				if(dstmac == NULL)
				{
					if (m_bPrintPackets) printf("IP not in file?\n");
				}
				else
				{
					//printf("Found Mac, copying it across!\n");
					memcpy((void*)buf, (void*)dstmac, 6);
				}//if found mac

			}// if ipv4
		}// if got table and processed frame



		//TX
		if (!drop)
		{
			if (m_bPrintPackets) printf("Injecting\n");
				pcap_inject(m_pDev, (void*)buf, size);
		}
		else
		{
			if (m_bPrintPackets) printf("Dropped\n");
		}


	}

	free(buf);
}

void InterfaceOutput::setDropRate(int dr)
{
	m_nDropRate = dr;
}

InterfaceOutput::~InterfaceOutput() {
	// TODO Auto-generated destructor stub

	free(m_sErrBuf);
}
