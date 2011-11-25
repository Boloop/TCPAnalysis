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
#include <pcap.h>  /* GIMME a libpcap plz! */
#include <errno.h>


class InterfaceInput {
private:
	char  		*m_sInterface;
	char 		*m_sErrBuf;
	pcap_t 		*m_pDev;


public:
	InterfaceInput(char*);
	bool open();

	virtual ~InterfaceInput();
};

#endif /* INTERFACEINPUT_H_ */
