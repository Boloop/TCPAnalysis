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
	m_bSignal = false;


}

void BufferQueue::setToSignal(bool val)
{
	/*
	 * Will enable/disable setting signal to be used for waitForData method
	 */

	m_bSignal = val;
}

bool BufferQueue::addOnTop(char* data, int size)
{
	/*
	 * Will try and copy the data on top of the buffer will return false if there is no space to add it
	 * otherwise true for success
	 *
	 * Ideally should call lock and unlock outside this method...!
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

	//Signal?
	if(m_bSignal)
		pthread_cond_signal(&m_CondDataAvail);

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

	free(dp.pData);

	return dp.nSize;

}

void BufferQueue::lock()
{
	pthread_mutex_lock(&m_Lock);
}

void BufferQueue::unlock()
{
	pthread_mutex_unlock(&m_Lock);
}

int BufferQueue::waitForData()
{
	/*
	 *  This will wait if there is any data in the buffer for one second
	 *  Will return the result of the Condition wait
	 *  0 = Data! Error otherwise (including timeout)
	 *
	 * You Must have already called the Lock Method! and checked that there is no data
	 * left, otherwise you may have packets stuck in the buffer not being read.
	 */
	struct timespec ts;
	clock_gettime(CLOCK_REALTIME, &ts);
	ts.tv_sec += 1;

	return pthread_cond_timedwait(&m_CondDataAvail, &m_Lock, &ts);

}

int BufferQueue::packetsInQueue()
{
	/*
	 * this will return the number of packets in the queue.
	 * Ideally, you should call the lock and unlock methods around this
	 */

	if (!m_queue->empty())
		return (int)m_queue->size();
	else
		return 0;
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


