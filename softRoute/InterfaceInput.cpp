/*
 * InterfaceInput.cpp
 *
 *  Created on: 25 Nov 2011
 *      Author: one
 */

#include "InterfaceInput.h"

InterfaceInput::InterfaceInput(char* interface) {
	// TODO Auto-generated constructor stub
	m_sErrBuf = (char*)malloc(PCAP_ERRBUF_SIZE);
	m_pDev = NULL;
	m_sInterface = interface;

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

InterfaceInput::~InterfaceInput() {
	// TODO Auto-generated destructor stub

	free(m_sErrBuf);
}
