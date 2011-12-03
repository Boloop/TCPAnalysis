/*
 * BufferQueue.h
 *
 *  This is a craft little class
 *  Basically is a buffer for packets, will copy them across if there is space.
 *
 *  Not thread safe (as of yet)!
 *
 *                          | - Where m_nTopIndex will be placed
 *   |<-- Packet 1 Data -->|<- Size of packet 1 ->|<-- Packet 2 Data -->|<- Size of packet 2 ->|....
 *
 */

#ifndef BUFFERQUEUE_H_
#define BUFFERQUEUE_H_


#include <stdlib.h>
#include <string.h>

class BufferQueue {
private:
	char * m_pBuffer;
	int    m_nCapacity;
	int    m_nTopIndex;
	int    m_nSizeSize; //Size of the integer used to measure a size of the packet in a buffer


public:
	BufferQueue(int size);

	bool addOnTop(char*, int);


	virtual ~BufferQueue();
};

#endif /* BUFFERQUEUE_H_ */
