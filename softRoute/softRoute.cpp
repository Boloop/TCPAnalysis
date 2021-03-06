
#include <time.h>
#include <unistd.h>
#include <string>
#include <iostream>

#include "InterfaceInput.h"
#include "InterfaceOutput.h"
#include "ArpTable.h"
#include "BufferQueue.h"

struct args
{
	char* sDev1;
	char* sDev2;
	char* sArpFile;
	bool bPrintArp;
	bool bPrintPacketsIn;
	bool bPrintPacketsOut;
	int nOutputRate;
	int nDropRate;
	int nDropRateBack;
	int nRetryLimit;
};

void intArgs(args *a)
{
	a->sDev1 = NULL;
	a->sDev2 = NULL;
	a->sArpFile = NULL;
	a->bPrintArp = false;
	a->bPrintPacketsIn = false;
	a->bPrintPacketsOut = false;
	a->nOutputRate = 0;
	a->nDropRate = 0; //
	a->nDropRateBack = 0;
	a->nRetryLimit = 0;
	

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


		// -or Output Rate in byte/sec!
		if ( strcmp (parg,"-or") == 0 ) // -or for Outputrate
		{
			if (argc != iend-1)
			{
				int rate = atoi (argv[i+1]);
				if (rate <= 0)
				{
					fprintf(stderr, "Output rate incorrect...\n");
					return false;
				}

				a->nOutputRate = rate;


				i++;
				continue;
			}
			else
			{
				fprintf(stderr, "Please enter a size for -or output rate\n");
				return false;
			}
		} // if -or


		// -dr Droprate out of 1000
		if ( strcmp (parg,"-dr") == 0 ) // -or for Outputrate
		{
			if (argc != iend-1)
			{
				int rate = atoi (argv[i+1]);
				if (rate <= 0)
				{
					fprintf(stderr, "Droprate -dr incorrect...\n");
					return false;
				}
				if(rate > 1000 || rate < 0)
				{
					fprintf(stderr, "Droprate -dr must be between 0-1000\n");
					return false;
				}

				a->nDropRate = rate;


				i++;
				continue;
			}
			else
			{
				fprintf(stderr, "Please enter a size for -dr output rate\n");
				return false;
			}
		} // if -dr
		
		
		

		// -drb DroprateBack out of 1000
		if ( strcmp (parg,"-drb") == 0 ) // -or for Outputrate
		{
			if (argc != iend-1)
			{
				int rate = atoi (argv[i+1]);
				//FIXME atoi outputs 0 on error, can't parse "0"... Fail
				if (rate <= 0)
				{
					fprintf(stderr, "Droprate -drb incorrect...\n");
					return false;
				}
				if(rate > 1000 || rate < 0)
				{
					fprintf(stderr, "Droprate -drb must be between 0-1000\n");
					return false;
				}
				a->nDropRateBack = rate;


				i++;
				continue;
			}
			else
			{
				fprintf(stderr, "Please enter a size for -drb output rate\n");
				return false;
			}
		} // if -drb

	
	
		// -rl Retry limit
		if ( strcmp (parg,"-rl") == 0 ) // -rl for retry limit
		{
			if (argc != iend-1)
			{
				int limit = atoi (argv[i+1]);
				if (limit <= 0)
				{
					fprintf(stderr, "Retry Limit -rl incorrect...\n");
					return false;
				}
				if(limit > 100 || limit < 0)
				{
					fprintf(stderr, "Retry Limit -rl must be between 0-100\n");
					return false;
				}

				a->nRetryLimit = limit;


				i++;
				continue;
			}
			else
			{
				fprintf(stderr, "Please enter a size for -rl retry Limit\n");
				return false;
			}
		} // if -rl

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

	//Seed the RNG
	srand(time(0));

	InterfaceInput::InterfaceInput* devLisOne = new InterfaceInput::InterfaceInput(a.sDev1);
	InterfaceOutput::InterfaceOutput* devInjOne = new InterfaceOutput::InterfaceOutput(a.sDev1);
	InterfaceInput::InterfaceInput* devLisTwo = new InterfaceInput::InterfaceInput(a.sDev2);
	InterfaceOutput::InterfaceOutput* devInjTwo = new InterfaceOutput::InterfaceOutput(a.sDev2);

	BufferQueue::BufferQueue * bqOneToTwo = new BufferQueue::BufferQueue(6400);
	BufferQueue::BufferQueue * bqTwoToOne = new BufferQueue::BufferQueue(6400);


	if(arpTable != NULL)
	{
		printf("Loading ARP table into output interfaces\n");
		devInjOne->setArpTable(arpTable);
		devInjTwo->setArpTable(arpTable);
	}

	if(a.bPrintPacketsOut)
	{
		printf("Setting to print packets on Outputs\n");
		devInjOne->setPrintPackets(true);
		devInjTwo->setPrintPackets(true);
	}

	if(a.bPrintPacketsIn)
	{
		printf("Setting to print packets on Outputs\n");
		devLisOne->setPrintPackets(true);
		devLisTwo->setPrintPackets(true);
	}

	if(a.nOutputRate != 0)
	{
		printf("Setting outputrate to %d byte/sec\n", a.nOutputRate);
		devInjOne->setOutputRate(a.nOutputRate);
		devInjTwo->setOutputRate(a.nOutputRate);
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

	if (a.nDropRate != 0)
	{
		printf("Setting droprate to %d/1000\n", a.nDropRate);
		devInjTwo->setDropRate(a.nDropRate);
		if (a.nDropRateBack != 0)
		{
			printf("Setting droprate-Back to %d/1000\n", a.nDropRateBack);
			devInjOne->setDropRate(a.nDropRateBack);
		}
		else
		{
			devInjOne->setDropRate(a.nDropRate);
		}

	}
	
	if(a.nRetryLimit > 0)
	{
		printf("Setting retryLimit to %d (forward Path only!)\n", a.nRetryLimit);
		devInjTwo->setRetryLimit(a.nRetryLimit);
	}

	//devInjOne->open();
	//devInjTwo->open();

	devInjOne->usePcap(devLisOne->givePcap());
	devInjTwo->usePcap(devLisTwo->givePcap());

	devInjOne->setBroadcast(true);
	devInjTwo->setBroadcast(true);

	//
	//Bridge
	//
	//devLisOne->bridgeWith(devInjTwo);
	//devLisTwo->bridgeWith(devInjOne);

	//
	//Buffer!
	//
	bqOneToTwo->setToSignal(true);
	bqTwoToOne->setToSignal(true);
	devInjOne->addInputBuffer(bqTwoToOne);
	devInjTwo->addInputBuffer(bqOneToTwo);
	devLisOne->pipeIntoBuffer(bqOneToTwo);
	devLisTwo->pipeIntoBuffer(bqTwoToOne);
	devInjOne->Start();
	devInjTwo->Start();




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

	devInjOne->kill();
	devInjTwo->kill();

	devInjOne->Join();
	devInjTwo->Join();


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
