/*
 * BufferQueue.h
 *
 *  This is a craft little class
 *  Basically is a buffer for packets, will copy them across if there is space.
 *
 *  Not thread safe (as of yet)!
 *
 *
 */

#ifndef BUFFERQUEUE_H_
#define BUFFERQUEUE_H_


#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <queue>



struct DataPacket {
   int nSize;
   char *pData;
};

class BufferQueue {
private:

	int    m_nCapacity; // The total overall size of the buffer
	int	   m_nUtilised; // The size of the buffer being used.

	pthread_mutex_t m_Lock;
	pthread_cond_t m_CondDataAvail;

	bool m_bSignal;


	std::queue<DataPacket> *m_queue;


public:
	BufferQueue(int size);

	bool addOnTop(char*, int);

	int removeFromBottom(char*);

	virtual ~BufferQueue();

	void lock();
	void unlock();
	int waitForData();
	int packetsInQueue();
	void setToSignal(bool val);
};

#endif /* BUFFERQUEUE_H_ */
