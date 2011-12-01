/*
 * ArpTable.cpp
 *
 *  See ArpTable.h for details
 */

#include "ArpTable.h"

ArpTable::ArpTable() {
	// Constructor, default values

	m_nMacIPCount = 0;
	m_nMacIPSize = 0;
	m_pMacIPs = NULL;


}

bool ArpTable::readFile(char* filepath)
{
	/*
	 * This will load in the file and statically assign these addresses
	 * in this class!
	 *
	 * return True for success, False for failure
	 */

	FILE *fp;

	fp = fopen(filepath, "r");

	if(fp == NULL)
	{
		fprintf(stderr, "Could not open the file %s\n", filepath);
		return false;
	}

	//Prepare to read
	int macIPSize = sizeof(macip);
	char* mbuf = (char*)malloc(macIPSize);
	size_t rtn;

	m_nMacIPSize = 16;
	m_pMacIPs = (macip**)malloc( sizeof( macip* ) * m_nMacIPSize );

	//For each entry!
	for(;;){
		rtn = fread(mbuf, 1, macIPSize, fp);
		//printf("returned %d\n", rtn);
		if (rtn != 10) //We have an error/eof?
		{
			printf("EOF/ERROR? Who knows ????\n");
			break; //'tis easy
		}

		if (m_nMacIPSize == m_nMacIPCount) //Do we have space to add it?
		{
			//So far, we could alloc more memory, for now, No :(
			fprintf(stderr, "Ran out of memory for ArpTable Entries loading file.\n");
			break;
		}

		//Join the memory! :)
		m_pMacIPs[m_nMacIPCount] = (macip*)mbuf;
		m_nMacIPCount++;

		//Alloc more memmory! D:
		mbuf = (char*)malloc(macIPSize);
	}


	free(mbuf); //we never use the last one.
	fclose(fp);
	return true;




}

void ArpTable::printTable(){
	/*
	 * Prints the values present in the table, mostly to check the integrity of the file loading
	 */

	int i;
	macip* ent;
	printf("Printing %d entries\n", m_nMacIPCount);
	for (i = 0; i < m_nMacIPCount; i++)
	{
		ent = m_pMacIPs[i];

		printf("IP: %d.%d.%d.%d MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", ent->ip4[0], ent->ip4[1], ent->ip4[2],
		      ent->ip4[3], ent->mac[0], ent->mac[1], ent->mac[2], ent->mac[3], ent->mac[4], ent->mac[5]);


	}

}

char* ArpTable::findMacFromIP(char* sIP)
{
	/*
	 * Will return prt to mac address of if in list!
	 * Null if it can not be found
	 */

	int i;
	for(i = 0; i < m_nMacIPCount; i++)
	{
		if (memcmp ( sIP, m_pMacIPs[i]->ip4, 4 ) == 0)
		{
			return m_pMacIPs[i]->mac;
		}
	}

	return NULL;



}

ArpTable::~ArpTable() {
	// destructor, freeing the memory slaves!

	int i;

	for(i=0; i<m_nMacIPCount; i++)
	{
		free(m_pMacIPs[i]);
	}

	free(m_pMacIPs);
}
