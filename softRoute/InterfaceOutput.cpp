/*
 * InterfaceOutput.cpp
 *
 *  Created on: 26 Nov 2011
 *      Author: one
 */

#include <stdio.h>
#include "InterfaceOutput.h"

InterfaceOutput::InterfaceOutput(char* interface) {
	// TODO Auto-generated constructor stub


	m_sErrBuf = (char*)malloc(PCAP_ERRBUF_SIZE);
	m_pDev = NULL;
	m_sInterface = interface;


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

void InterfaceOutput::inject(u_char* data, int len)
{
	/*
	 * Will inject the data! :D
	 */

	pcap_inject(m_pDev, (void*)data, len);
}

InterfaceOutput::~InterfaceOutput() {
	// TODO Auto-generated destructor stub

	free(m_sErrBuf);
}
