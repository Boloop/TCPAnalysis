/*
 * BufferQueue.h
 *
 *  This is a craft little class
 *  Basically is a buffer for packets, will copy them across if there is space.
 *
 *  Not thread safe (as of yet)!
 *
 *              Where m_nTopIndex will be placed ->|
 *   |<-- Size of packet 1 -->|<- Packet 1 data ->|<-- Size of packet 2 -->|<- Packet 2 Data ->|....
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
	int   *m_pTopPacketSize;


public:
	BufferQueue(int size);

	bool addOnTop(char*, int);

	int removeFromBottom(char);

	virtual ~BufferQueue();
};

#endif /* BUFFERQUEUE_H_ */
