
#include <time.h>
#include <unistd.h>

#include "InterfaceInput.h"
#include "InterfaceOutput.h"


int main(int argc, char **argv)
{

  	//InterfaceInput::printDevs();

	if(argc < 3)
	{
		fprintf(stderr, "Please use [ethX] [ethY] to bridge\n");
		return -1;
	}

	char* devOne = argv[1];
	char* devTwo = argv[2];


	char* devLisName = "eth0";

	InterfaceInput::InterfaceInput* devLisOne = new InterfaceInput::InterfaceInput(devOne);
	InterfaceOutput::InterfaceOutput* devInjOne = new InterfaceOutput::InterfaceOutput(devOne);
	InterfaceInput::InterfaceInput* devLisTwo = new InterfaceInput::InterfaceInput(devTwo);
	InterfaceOutput::InterfaceOutput* devInjTwo = new InterfaceOutput::InterfaceOutput(devTwo);

	if(!devLisOne->open())
	{
		//Failed :(
		return -1;
	}
	else
	{
		printf("Now Opened Input %s\n", devLisName);
	}

	if(!devLisTwo->open())
	{
		return -1;
	}
	else
	{
		printf("Now Opened Input %s\n", devLisName);
	}

	//devInjOne->open();
	//devInjTwo->open();

	devInjOne->usePcap(devLisOne->givePcap());
	devInjTwo->usePcap(devLisTwo->givePcap());


	devLisOne->bridgeWith(devInjTwo);
	devLisTwo->bridgeWith(devInjOne);

	printf("Listening for 10 seconds\n");

	devLisOne->Start();
	devLisTwo->Start();
	struct timespec t;
	t.tv_sec = 10;
	t.tv_nsec = 0;

	//nanosleep(&t);
	usleep(10000000);
	printf ("Killing\n");
	devLisOne->kill();
	devLisTwo->kill();

	devLisOne->Join();
	devLisTwo->Join();

	delete devLisOne;
	delete devInjOne;
	delete devLisTwo;
	delete devInjTwo;

  	return 0;
}
