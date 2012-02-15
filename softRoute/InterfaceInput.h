/*
 * InterfaceInput.h
 *
 *  Created on: 25 Nov 2011
 *      Author: one
 */

#ifndef INTERFACEINPUT_H_
#define INTERFACEINPUT_H_


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pcap.h>  /* GIMME a libpcap plz! */
#include <errno.h>
extern "C" {
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <arpa/inet.h>

	#include <pthread.h>
}

#include "MyThread.h"
#include "InterfaceOutput.h"
#include "BufferQueue.h"

class InterfaceInput: public MyThread {
private:
	char  				*m_sInterface;
	char 				*m_sErrBuf;
	pcap_t 				*m_pDev;

	uint32_t 			m_nPackets;
	uint32_t 			m_nPData;

	bool				 m_bIsDead;
	pthread_mutex_t 	 m_lock;

	InterfaceOutput::InterfaceOutput *m_pBridgeOutput;

	BufferQueue *		m_pBufferQueue;

	bool				 m_bPrintPackets;

public:
	InterfaceInput(char*);
	bool open();
	void Execute();
	void kill();
	pcap_t* givePcap();

	void bridgeWith(InterfaceOutput::InterfaceOutput*);
	void pipeIntoBuffer(BufferQueue *bq);

	void setPrintPackets(bool);

	virtual ~InterfaceInput();



	static void gotPacket(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);

	static void printDevs();
};

#endif /* INTERFACEINPUT_H_ */
