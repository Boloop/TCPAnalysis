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
extern "C" {
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <arpa/inet.h>

	#include <pthread.h>
}



class InterfaceOutput {
private:
	char  				*m_sInterface;
	char 				*m_sErrBuf;
	pcap_t 				*m_pDev;

public:
	InterfaceOutput(char*);
	void inject(u_char*, int);
	bool open();
	void usePcap(pcap_t*);


	virtual ~InterfaceOutput();

};

#endif /* INTERFACEOUTPUT_H_ */
