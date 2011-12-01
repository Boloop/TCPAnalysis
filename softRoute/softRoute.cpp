
#include <time.h>
#include <unistd.h>
#include <string>
#include <iostream>

#include "InterfaceInput.h"
#include "InterfaceOutput.h"
#include "ArpTable.h"

struct args
{
	char* sDev1;
	char* sDev2;
	char* sArpFile;
	bool bPrintArp;
	bool bPrintPacketsIn;
	bool bPrintPacketsOut;
};

void intArgs(args *a)
{
	a->sDev1 = NULL;
	a->sDev2 = NULL;
	a->sArpFile = NULL;
	a->bPrintArp = false;
	a->bPrintPacketsIn = false;
	a->bPrintPacketsOut = false;

}

bool readArgs(args *a, int argc, char **argv)
{
	if(argc < 3)
	{
		fprintf(stderr, "Please use [ethX] [ethY] to bridge\n");
		return false;
	}

	a->sDev1 = argv[argc-2];
	a->sDev2 = argv[argc-1];

	int i;
	int iend = argc-2;
	char *parg;
	for (i=0; i<iend; i++)
	{
		parg = argv[i];

		// -a ARP TABLE FILE
		if ( strcmp (parg,"-a") == 0 ) // -a for arptable!
		{
			if (argc != iend-1)
			{
				a->sArpFile = argv[i+1];
				i++;
				continue;
			}
			else
			{
				fprintf(stderr, "Please enter a path for -a Arp table file\n");
				return false;
			}
		} // if -a

		// -pa Print ARP TABLE!
		if ( strcmp (parg,"-pa") == 0 )
		{
			a->bPrintArp = true;
		}

		// -pip Print input packets!
		if ( strcmp (parg,"-pip") == 0 )
		{
			a->bPrintPacketsIn = true;
		}

		// -pop Print output packets!
		if ( strcmp (parg, "-pop") == 0 )
		{
			a->bPrintPacketsOut = true;
		}

	}// for each arg

	return true;

}


int main(int argc, char **argv)
{

  	//InterfaceInput::printDevs();

	args a;
	intArgs(&a);

	if(!readArgs(&a, argc, argv))
	{
		fprintf(stderr, "Could not parse args, QUITING\n");
		return -1;
	}

	//Load arpTable? :o
	ArpTable::ArpTable* arpTable = NULL;
	if(a.sArpFile != NULL)
	{
			arpTable = 	new ArpTable::ArpTable();

			if (!arpTable->readFile(a.sArpFile)) //Error :(
			{
				fprintf(stderr, "Problem opening Arp file, QUITTING\n");
				return -1;
			}

			if (a.bPrintArp)
			{
				arpTable->printTable();
				return -1;
			}
	}



	InterfaceInput::InterfaceInput* devLisOne = new InterfaceInput::InterfaceInput(a.sDev1);
	InterfaceOutput::InterfaceOutput* devInjOne = new InterfaceOutput::InterfaceOutput(a.sDev1);
	InterfaceInput::InterfaceInput* devLisTwo = new InterfaceInput::InterfaceInput(a.sDev2);
	InterfaceOutput::InterfaceOutput* devInjTwo = new InterfaceOutput::InterfaceOutput(a.sDev2);


	if(a.bPrintPacketsOut)
	{
		devInjOne->setPrintPackets(true);
		devInjTwo->setPrintPackets(true);
	}


	if(!devLisOne->open())
	{
		//Failed :(
		return -1;
	}
	else
	{
		printf("Now Opened Input %s\n", a.sDev1);
	}

	if(!devLisTwo->open())
	{
		return -1;
	}
	else
	{
		printf("Now Opened Input %s\n", a.sDev2);
	}

	//devInjOne->open();
	//devInjTwo->open();

	devInjOne->usePcap(devLisOne->givePcap());
	devInjTwo->usePcap(devLisTwo->givePcap());

	devInjOne->setBroadcast(true);
	devInjTwo->setBroadcast(true);

	devLisOne->bridgeWith(devInjTwo);
	devLisTwo->bridgeWith(devInjOne);

	//printf("Listening for 10 seconds\n");

	devLisOne->Start();
	devLisTwo->Start();
	struct timespec t;
	t.tv_sec = 10;
	t.tv_nsec = 0;

	//nanosleep(&t);
	//usleep(10000000);


	std::string userinput;

	std::cout << "Press Enter to Quit" << std::endl;
	std::cin >> userinput;

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
