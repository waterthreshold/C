#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#include "logger.h"
void usage(const char *prog)
{
    printf("Usage: %s -p <port> -r <ip> <msg>\n", prog);
    printf("Example: %s -p 8080 -r 192.168.1.100 \"Hello world!\"", prog);
}

int main(int argc, char *argv[])
{
    int opt;
    int port = 514;
    char *ip = "192.168.100.3";
	char *msg=NULL;
    while ((opt = getopt(argc, argv, "p:r:")) != -1)
    {
        switch (opt)
        {
            case 'p':
                port = atoi(optarg);
                break;
			case 'r':
				ip=optarg;
				break;
            default:
                usage(argv[0]);
                return 1;
        }
    }

    /* Remaining argument should be IP */
    if (optind < argc)
    {
        msg = argv[optind];
    }

    if (port <= 0 || ip == NULL)
    {
        usage(argv[0]);
        return 1;
    }

    /* Validate IP address */
    struct sockaddr_in sa;
    if (inet_pton(AF_INET, ip, &(sa.sin_addr)) != 1)
    {
        printf("Invalid IP address: %s\n", ip);
        return 1;
    }

//    printf("Port : %d\n", port);
//    printf("IP   : %s\n", ip);
	send_syslog(ip,port,msg);
    return 0;
}
