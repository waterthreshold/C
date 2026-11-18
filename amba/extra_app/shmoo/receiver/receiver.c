#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

#define PORT 6868
#define BUFFER_SIZE 1024

int main()
{
    int sockfd;
    struct sockaddr_in server_addr, client_addr;
    socklen_t addr_len = sizeof(client_addr);
    char buffer[BUFFER_SIZE];

    // Create UDP socket
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket failed");
        exit(1);
    }

    // Bind to all interfaces
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind failed");
        close(sockfd);
        exit(1);
    }

    printf("UDP server listening on port %d...\n", PORT);

    // Persistent loop
    while (1) {
        memset(buffer, 0, BUFFER_SIZE);

        int len = recvfrom(sockfd, buffer, BUFFER_SIZE - 1, 0,
                           (struct sockaddr *)&client_addr, &addr_len);

        if (len < 0) {
            perror("recvfrom failed");
            continue;
        }

        buffer[len] = '\0';

        // Get client IP
        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));

        printf("\nReceived from %s:%d\n", client_ip, ntohs(client_addr.sin_port));
        printf("Raw message: %s\n", buffer);

        // Parse format: path,crc
        char *path = strtok(buffer, " ");
        char *crc  = strtok(NULL, " ");

        if (path && crc) {
            printf("Parsed Path: %s\n", path);
            printf("Parsed CRC : %s\n", crc);
        } else {
            printf("Invalid format!\n");
        }
    }

    close(sockfd);
    return 0;
}
