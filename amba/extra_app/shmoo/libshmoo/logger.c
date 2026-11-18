#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <time.h>

#include "utils.h"
// #define NETWORK_INTERFACE "eth0"

void send_syslog(char *host, int port, const char *message)
{
    int sock;
    struct sockaddr_in server_addr;
    char buffer[1024];
	char hostname[1024];
	char ip[1024];
	get_hostname(hostname);
	get_ip(ip,1024);
    // Create UDP socket
    sock = socket(AF_INET, SOCK_DGRAM, 0);

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &server_addr.sin_addr);

    // Create timestamp
    time_t now = time(NULL);
    struct tm *t = localtime(&now);

    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%b %d %H:%M:%S", t);
	
    // Syslog message format (RFC3164)
    int priority = 13; // user-level + notice
    snprintf(buffer, sizeof(buffer),
             "<%d>%s %s(%s): %s",
             priority, timestamp, hostname, ip, message);

    // Send message
    sendto(sock, buffer, strlen(buffer), 0,
           (struct sockaddr *)&server_addr,
           sizeof(server_addr));

    close(sock);
}

