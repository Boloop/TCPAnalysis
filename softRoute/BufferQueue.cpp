/*
 * BufferQueue.cpp
 *
 *  See BufferQueue.h for more details
 */

#include "BufferQueue.h"

BufferQueue::BufferQueue(int size) {
	//  constructor stub

	m_nCapacity = size;
	m_nUtilised = 0;
	m_queue = new std::queue<DataPacket>();

	m_Lock = PTHREAD_MUTEX_INITIALIZER;
	m_CondDataAvail = PTHREAD_COND_INITIALIZER;


}

bool BufferQueue::addOnTop(char* data, int size)
{
	/*
	 * Will try and copy the data on top of the buffer will return false if there is no space to add it
	 * otherwise true for success
	 */

	//Do we have the space?
	int spaceLeft = m_nCapacity-m_nUtilised;

	if (spaceLeft < size) // No space :(
		return false;

	//Copy across! SHINJI!
	char* newData = (char*)malloc(size);
	memcpy((void*)newData, (void*)data, size);

	DataPacket dp;
	dp.nSize = size;
	dp.pData = newData;

	m_queue->push(dp);

	return true;

}

int BufferQueue::removeFromBottom(char* newData)
{
	/*
	 * Will copy (if anything) into the char* buffer of what is next to be served in the kitchen
	 * 0 = Empty, Nada, nothing!
	 */


	if(m_queue->empty())
		return 0;


	DataPacket dp = m_queue->front();
	memcpy((void*)newData, (void*)dp.pData, dp.nSize);
	m_queue->pop();

	return dp.nSize;

}

BufferQueue::~BufferQueue() {
	// destructor stub

	while(!m_queue->empty())
	{
		DataPacket dp = m_queue->front();
		free(dp.pData);
		m_queue->pop();
	}


	delete m_queue;
}
