/*
 * MyThread.cpp
 *
 *  Created on: 28 Feb 2011
 *      Author: two
 */

#include "MyThread.h"

MyThread::MyThread() {}

int MyThread::Start()
{
	/*
	 * This will create and start the thread
	 */
   //Arg(arg); // store user data
   int code;

   code = pthread_create( &m_selfThread, NULL, MyThread::EntryPoint, (void*) this);
   //code = thread_create(MyThread::EntryPoint, this, & ThreadId_);
   return code;
}

int MyThread::Run()
{
	/*
	 * This is the order the code should be run it, Setup then Execute
	 *  Where Setup is the initialising of the thread (done in it's own
	 *  thread from the parent that created it) and then Execute which
	 *  usually contains a loop (maybe not)
	 */
   Setup();
   Execute();
   return 0;
}

/*static */
void * MyThread::EntryPoint(void * pthis)
{
	/*
	 * this is the method used in the pthread_create() will convert the pointer type
	 * to this class type and start the actual code.
	 */
   MyThread * pt = (MyThread*)pthis;
   pt->Run();

   return NULL;
}


void MyThread::Setup()
{
        /*
         * the General initialisation of the thread, kept here for best practice
         * although I don't use it much
         */
}

void MyThread::Execute()
{
        /*
         * Our code goes here!
         */
}

void MyThread::Join()
{
	/*
	 * This is used for the parent thread and waits for it's child thread to join
	 * i.e. the parent thread will be blocked and will resume once the child has
	 * finished running setup() and execute() methods.
	 *
	 */
	pthread_join( m_selfThread, NULL);
}


MyThread::~MyThread() {
	// TODO Auto-generated destructor stub
}
