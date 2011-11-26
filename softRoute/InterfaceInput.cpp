/*
 * InterfaceInput.cpp
 *
 *  Created on: 25 Nov 2011
 *      Author: one
 */
#include <stdio.h>
#include "InterfaceInput.h"

InterfaceInput::InterfaceInput(char* interface) {
	// TODO Auto-generated constructor stub
	m_sErrBuf = (char*)malloc(PCAP_ERRBUF_SIZE);
	m_pDev = NULL;
	m_sInterface = interface;
	m_bIsDead = false;
	m_lock = PTHREAD_MUTEX_INITIALIZER;

	m_nPackets = 0;
	m_nPData = 0;

	m_pBridgeOutput = NULL;

}

bool InterfaceInput::open()
{
	/*
	 * This will open up the pcap interface, boolean if successful or not
	 * true = :) , false = :(
	 */


	m_pDev = pcap_open_live(m_sInterface, BUFSIZ, 1, 1000, m_sErrBuf);
	if(m_pDev == NULL)
	{
		fprintf(stderr, "Unable to listen to device: %s : %s\n", m_sInterface, m_sErrBuf);
		return false;
	}
	return true;




}

pcap_t* InterfaceInput::givePcap()
{

	/*
	 * This will give out the handler, best after it's open ;)
	 */
	return m_pDev;

}

void InterfaceInput::Execute()
{
	/*
	 * Loop until we get dizzy!
	 */

	for(;;)
	{
		//Shall we stop looping yet?
		pthread_mutex_lock( &m_lock );
		if(m_bIsDead)
		{
			//We're dead, go and die :(
			pthread_mutex_unlock( &m_lock );
			break;
		}

		pthread_mutex_unlock( &m_lock );

		//Do part of the loop!
		pcap_loop(m_pDev, 100, InterfaceInput::gotPacket, (u_char*)this);

	}

}

void InterfaceInput::kill()
{
	/*
	 * This will set the isDead to true, to stop the thread
	 */

	pthread_mutex_lock( &m_lock );
	m_bIsDead = true;
	pcap_breakloop(m_pDev);
	pthread_mutex_unlock( &m_lock );

	printf("Sent %d Pkts. Total data: %d Bytes\n", m_nPackets, m_nPData);
}



void InterfaceInput::bridgeWith(InterfaceOutput::InterfaceOutput* outputdev)
{
	/*
	 * This will basically inject all packets onto this interface,
	 * useful for rudimentary testing
	 */

	m_pBridgeOutput = outputdev;

}


InterfaceInput::~InterfaceInput() {
	// TODO Auto-generated destructor stub

	free(m_sErrBuf);
}



void InterfaceInput::printDevs()
{
	/*
	 * this will print out a list of devs! :)
	 */


	char *dev; /* name of the device to use */
	char *net; /* dot notation of the network address */
	char *mask;/* dot notation of the network mask    */
	int ret;   /* return code */
	char errbuf[PCAP_ERRBUF_SIZE];
	bpf_u_int32 netp; /* ip          */
	bpf_u_int32 maskp;/* subnet mask */
	struct in_addr addr;

	pcap_if_t *devlist;
 	//int pcap_findalldevs(pcap_if_t **alldevsp, char *errbuf)

 	ret = pcap_findalldevs(&devlist, errbuf);

  	if(ret == -1){
  		//error :(
  		printf("Error, could not enumerate devs: %s\n", errbuf);
  		exit(-1);
  	}

  	if (devlist == NULL)
  	{
  		printf("Error, could not see any available devs\n");
  		exit(-1);
  	}

  	pcap_if_t *pdev = devlist;

  	//Does net need memories?
  	net = (char*)malloc(1024);
  	//memset(net, 0x00, 1024);
  	strncpy(net, "LOL", 10);
  	while(pdev != NULL)
  	{
  		printf("%s\n", pdev->name);
  		if (pdev->description != NULL)
  			printf("\t%s\n", pdev->description);

  		if (pdev->addresses != NULL)
  		{
  			printf("\tHas addesses\n");
  			pcap_addr_t *padd = pdev->addresses;

  			while(padd != NULL)
  			{
  				//net = inet_ntop(padd->addr);
  				if (padd->addr->sa_family == AF_INET)
  				{
  					//net = "IPv4";
  					printf("\tAdd4\n");
  					inet_ntop(AF_INET, padd->addr->sa_data, net, INET_ADDRSTRLEN);
  				}
  				else if (padd->addr->sa_family == AF_INET6)
  				{
  					//net = "IPv6";
  					printf("\tAdd6\n");
  					inet_ntop(AF_INET6, padd->addr->sa_data, net, INET6_ADDRSTRLEN);
  				}
  				else
  				{
  					printf("\tAddX\n");
  					//net = "Bigger";
  				}
  				printf("\t%s\n", net);
  				//printf("\tAdd\n");
  				padd = padd->next;
  			} // for each address

  		}//If address not null

  		pdev = pdev->next;

  	}// While (going through dev list)

  	free(net);
}

void InterfaceInput::gotPacket(u_char *args, const struct pcap_pkthdr *header, const u_char *packet)
{
	/*
	 * This will handle what to do when we gets a packet!
	 */
	InterfaceInput* self = (InterfaceInput*) args;
	//printf("GP : %n\n", (int)header->len);

	//printf("GP: %d %s %d\n", ++self->m_nPackets, self->m_sInterface, header->len);
	self->m_nPData += header->len;
	//printf("Got\n");

	//Bridging mode?
	if (self->m_pBridgeOutput != NULL)
	{
		//Special Delivery!
		self->m_pBridgeOutput->inject((u_char*)packet, header->len);
		//pcap_inject(self->m_pBridgeOutput, packet, header->len);


	}

}

