/*
 * BufferQueue.cpp
 *
 *  See BufferQueue.h for more details
 */

#include "BufferQueue.h"

BufferQueue::BufferQueue(int size) {
	//  constructor stub

	m_nCapacity = size;
	if (m_nCapacity < 128)
	{
		/*
		 * What do we DO!?!?!?!?
		 */
		return; // Segfault with style
	}

	m_pBuffer = (char*)malloc(m_nCapacity);
	m_nTopIndex = 0;
	m_nSizeSize = sizeof(int);
	m_pTopPacketSize = (int*)m_pBuffer;
	*m_pTopPacketSize = 0;


}

bool BufferQueue::addOnTop(char* data, int size)
{
	/*
	 * Will try and copy the data on top of the buffer will return false if there is no space to add it
	 * otherwise true for success
	 */

	//Do we have the space?
	int spaceLeft = m_nCapacity-m_nTopIndex-m_nSizeSize;

	if (spaceLeft < size) // No space :(
		return false;

	//Copy across! (There is a god if this works, not that I have no faith in my own abilities...)
	char* cpyPointer = m_pBuffer+m_nTopIndex+m_nSizeSize;
	memcpy((void*)cpyPointer, (void*)data, size);
	int* bufsize = (int*) (cpyPointer+size);
	*bufsize = size;


	return true;

}

BufferQueue::~BufferQueue() {
	// destructor stub
}
