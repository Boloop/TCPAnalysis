/*
 * MyThread.h
 *
 *  Created on: 28 Feb 2011
 *      Author: two
 *
 *      Mostly Followed from this: http://www.linuxselfhelp.com/HOWTO/C++Programming-HOWTO-18.html
 *      The only time I will have captilised function names! Gah
 *
 *      and I <3 my linux nerd yolinux site.
 *      http://www.yolinux.com/TUTORIALS/LinuxTutorialPosixThreads.html
 *
 *      To use:
 *      Overide Setup as setup
 *      Overide Execute as the main code of the thread to run.
 *
 *      to start the thread. Just call threadObject->Start();
 */

#ifndef MYTHREAD_H_
#define MYTHREAD_H_

extern "C" {
	#include <pthread.h>
}


class MyThread {
public:
	  MyThread();
      int Start();
      void Join();
      virtual ~MyThread();

  protected:
      int Run();
      static void * EntryPoint(void*);
      virtual void Setup();
      virtual void Execute();

      void * Arg() const {return Arg_;}
      void Arg(void* a){Arg_ = a;}
  private:
      pthread_t m_selfThread;
      void * Arg_;
};

#endif /* MYTHREAD_H_ */
