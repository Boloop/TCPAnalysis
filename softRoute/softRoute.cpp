#include <stdio.h>
#include <stdlib.h>
#include <pcap.h>  /* GIMME a libpcap plz! */
#include <errno.h>
extern "C" {
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
}

int main(int argc, char **argv)
{
 	char *dev; /* name of the device to use */ 
 	char *net; /* dot notation of the network address */
 	char *mask;/* dot notation of the network mask    */
 	int ret;   /* return code */
 	char errbuf[PCAP_ERRBUF_SIZE];
 	bpf_u_int32 netp; /* ip          */
 	bpf_u_int32 maskp;/* subnet mask */
 	struct in_addr addr;
 	
 	pcap_if_t *devlist;

 	//int pcap_findalldevs(pcap_if_t **alldevsp, char *errbuf)
  	
  	ret = pcap_findalldevs(&devlist, errbuf);
  	
  	if(ret == -1){
  		//error :(
  		printf("Error, could not enumerate devs: %s\n", errbuf);
  		exit(-1);
  	}
  	
  	if (devlist == NULL)
  	{
  		printf("Error, could not see any available devs\n");
  		exit(-1);
  	}
  	
  	pcap_if_t *pdev = devlist;
  	
  	while(pdev != NULL)
  	{
  		printf("%s\n", pdev->name);
  		if (pdev->description != NULL)
  			printf("\t%s\n", pdev->description);
  			
  		if (pdev->addresses != NULL)
  		{
  			printf("\tHasaddesses\n");
  			pcap_addr_t *padd = pdev->addresses;
  			
  			while(padd != NULL)
  			{
  				//net = inet_ntop(padd->addr);
  				if (padd->addr->sa_family == AF_INET)
  					inet_ntop(AF_INET, padd->addr->sa_data, net, INET_ADDRSTRLEN);
  				else if (padd->addr->sa_family == AF_INET6)
  					inet_ntop(AF_INET6, padd->addr->sa_data, net, INET6_ADDRSTRLEN);
  				printf("\t%s\n", net);
  				padd = padd->next;
  			}
  		}
  		pdev = pdev->next;
  	}
  	
  	return 0;
}
