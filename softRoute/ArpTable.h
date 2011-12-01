/*
 * ArpTable.h
 *
 *  This Will be a simple look up class for IPs (v4) to MACs
 *  Doesn't really implement ARP at this time. Statically
 *  loads in a list by a file for the time being.
 */

#ifndef ARPTABLE_H_
#define ARPTABLE_H_

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct macip
{
	char ip4[4];
	char mac[6];

};


class ArpTable {

private:
	macip ** m_pMacIPs;
	int		m_nMacIPCount;
	int		m_nMacIPSize;

public:
	ArpTable();
	bool readFile(char*);
	char* findMacFromIP(char*);
	void printTable();
	virtual ~ArpTable();
};

#endif /* ARPTABLE_H_ */
