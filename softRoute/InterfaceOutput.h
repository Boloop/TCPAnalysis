/*
 * InterfaceOutput.h
 *
 *  Created on: 26 Nov 2011
 *      Author: one
 */

#ifndef INTERFACEOUTPUT_H_
#define INTERFACEOUTPUT_H_


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pcap.h>  /* GIMME a libpcap plz! */
#include <errno.h>
#include <sys/time.h>
extern "C" {
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <arpa/inet.h>

	#include <pthread.h>

	#include <unistd.h>
}


#include "WTPacket.h"
#include "ArpTable.h"
#include "BufferQueue.h"
#include "MyThread.h"


class InterfaceOutput : public MyThread {
private:
	char  				*m_sInterface;
	char 				*m_sErrBuf;
	pcap_t 				*m_pDev;

	int 				 m_nOutputRate; // byte/sec. 0 = none/unlimited.
	timeval 			 m_tvNextPacket; // Time that next packet has to be sent after!

	bool				 m_bInjectWithBroadcast;

	bool				 m_bPrintPackets;

	ArpTable            *m_pArpTable;

	BufferQueue			*m_pBufferQueue;
	bool				 m_bIsDead;


public:
	InterfaceOutput(char*);
	void inject(u_char*, int);
	void setBroadcast(bool);
	bool open();
	void usePcap(pcap_t*);

	void setPrintPackets(bool);
	void setOutputRate(int);

	void setUpBufferWithSize(int);

	void setArpTable(ArpTable*);
	virtual ~InterfaceOutput();

	//bool open();
	void addInputBuffer(BufferQueue * bq);
	void Execute();
	void kill();

};

#endif /* INTERFACEOUTPUT_H_ */
