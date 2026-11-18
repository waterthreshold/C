#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <errno.h>

#define IPADDR_LEN		4
#define NETMASK_LEN		4
#define ETHERADDR_LEN	6
#define GWADDR_LEN		4
#define DNSADDR_LEN		4
// 1. Get IP Address (copies 4 raw bytes into p)
int GetIp(char *p, const char *intface) 
{
    int fd;
    struct ifreq ifr;
    
    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return -1;
    
    ifr.ifr_addr.sa_family = AF_INET;
    strncpy(ifr.ifr_name, intface, IFNAMSIZ - 1);
    
    if (ioctl(fd, SIOCGIFADDR, &ifr) < 0) 
    {
        close(fd);
        return -1;
    }
    
    close(fd);
    struct sockaddr_in *s = (struct sockaddr_in *)&ifr.ifr_addr;
    memcpy(p, &s->sin_addr.s_addr, IPADDR_LEN);
    return 0;
}

// 2. Get Netmask (copies 4 raw bytes into p)
int GetNetMask(char *p, const char *intface) 
{
    int fd;
    struct ifreq ifr;
    
    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return -1;
    
    ifr.ifr_addr.sa_family = AF_INET;
    strncpy(ifr.ifr_name, intface, IFNAMSIZ - 1);
    
    if (ioctl(fd, SIOCGIFNETMASK, &ifr) < 0) 
    {
        close(fd);
        return -1;
    }
    
    close(fd);
    struct sockaddr_in *s = (struct sockaddr_in *)&ifr.ifr_addr;
    memcpy(p, &s->sin_addr.s_addr, 4);
    return 0;
}

// 3. Get MAC / Ethernet Address (copies 6 raw bytes into p)
int GetEthrAddr(char *p, const char *intface) 
{
    int fd;
    struct ifreq ifr;
    
    fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return -1;
    
    strncpy(ifr.ifr_name, intface, IFNAMSIZ - 1);
    
    if (ioctl(fd, SIOCGIFHWADDR, &ifr) < 0) 
    {
        close(fd);
        return -1;
    }
    
    close(fd);
    memcpy(p, ifr.ifr_hwaddr.sa_data, ETHERADDR_LEN);
    return 0;
}

// 4. Get Default Gateway by parsing /proc/net/route (copies 4 raw bytes into p)
int GetGw(char *p, const char *intface) 
{
    FILE *fp = fopen("/proc/net/route", "r");
    if (!fp) return -1;

    char line[100];
    int found = -1;

    // Skip header line
    char *skip_header = fgets(line, sizeof(line), fp);

    while (fgets(line, sizeof(line), fp)) 
    {
        char iface_name[32];
        unsigned long dest, gateway;
        
        if (sscanf(line, "%s %lx %lx", iface_name, &dest, &gateway) == 3) 
        {
            if (strcmp(iface_name, intface) == 0 && dest == 0) // Default route destination is 0
            {
                memcpy(p, &gateway, GWADDR_LEN);
                found = 0;
                break;
            }
        }
    }

    fclose(fp);
    return found;
}

// 5. Get DNS IP by parsing /proc/resolv.conf or /etc/resolv.conf (copies 4 raw bytes into p)
int GetDns(char *p, const char *intface, int index) 
{
    (void)intface; // Unused parameter, system resolv.conf applies globally
    FILE *fp = fopen("/etc/resolv.conf", "r");
    if (!fp) return -1;

    char line[128];
    int found = 0;

    while (fgets(line, sizeof(line), fp)) 
    {
        char keyword[16];
        char ip_str[32];
		
        if (sscanf(line, "%s %s", keyword, ip_str) == 2) 
        {
            if (strcmp(keyword, "nameserver") == 0) 
            {
                struct in_addr addr;
                if (inet_pton(AF_INET, ip_str, &addr) == 1) 
                {
					found ++;
					if ( found == index ) {
						memcpy(p, &addr.s_addr, DNSADDR_LEN);
                    	break; // Grab the first nameserver
					}
					else {
						continue;
					}
                   
                }
            }
        }
    }

    fclose(fp);
    return found;
}

int GetHostName(char *p, size_t maxlen) 
{
    if (gethostname(p, maxlen) < 0) 
    {
        return -1;
    }
    // Ensure null-termination
    p[maxlen - 1] = '\0';
    return 0;
}

int apply_hostname_confing(const char *name, size_t len) {
    char current_hostname[256];
    char new_hostname[256];

    if (len == 0 || len >= sizeof(new_hostname)) {
        return -1; // Invalid length
    }

    // Extract and clean the incoming name
    size_t clean_len = 0;
    for (size_t i = 0; i < len; i++) {
        if (name[i] == '\0') {
            break;
        }
        new_hostname[clean_len++] = name[i];
    }
    new_hostname[clean_len] = '\0';

    if (clean_len == 0) {
        return -1; // Empty hostname
    }

    // Get current system hostname
    if (gethostname(current_hostname, sizeof(current_hostname)) != 0) {
        perror("gethostname failed");
        return -1;
    }

    // Compare and update if different
    if (strcmp(current_hostname, new_hostname) != 0) {
        printf("Updating hostname from '%s' to '%s'...\n", current_hostname, new_hostname);
        
        if (sethostname(new_hostname, clean_len) != 0) {
            perror("sethostname failed");
            return -1;
        }

        // Persist to file
        FILE *f = fopen("/etc/hostname", "w");
        if (f != NULL) {
            fprintf(f, "%s\n", new_hostname);
            fclose(f);
        }
    }

    return 0;
}


int apply_network_interface(const uint8_t *ip_bytes, const uint8_t *netmask_bytes, const char *iface_name) {
    int sockfd;
    struct ifreq ifr;
    struct sockaddr_in *sin;

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Socket creation failed");
        return -1;
    }

    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, iface_name, IFNAMSIZ - 1);

    // 1. Set IP Address via direct memory copy (no string conversion needed)
    sin = (struct sockaddr_in *)&ifr.ifr_addr;
    sin->sin_family = AF_INET;
    memcpy(&sin->sin_addr.s_addr, ip_bytes, 4);

    if (ioctl(sockfd, SIOCSIFADDR, &ifr) < 0) {
        perror("ioctl SIOCSIFADDR failed");
        close(sockfd);
        return -1;
    }

    // 2. Set Subnet Mask via direct memory copy
    sin = (struct sockaddr_in *)&ifr.ifr_netmask;
    sin->sin_family = AF_INET;
    memcpy(&sin->sin_addr.s_addr, netmask_bytes, 4);

    if (ioctl(sockfd, SIOCSIFNETMASK, &ifr) < 0) {
        perror("ioctl SIOCSIFNETMASK failed");
        close(sockfd);
        return -1;
    }

    // 3. Ensure interface flags are UP and RUNNING
    if (ioctl(sockfd, SIOCGIFFLAGS, &ifr) == 0) {
        ifr.ifr_flags |= (IFF_UP | IFF_RUNNING);
        ioctl(sockfd, SIOCSIFFLAGS, &ifr);
    }

    close(sockfd);
    
    // Debug print
	#ifdef DEBUG
    struct in_addr ip_dbg, mask_dbg;
    memcpy(&ip_dbg.s_addr, ip_bytes, 4);
    memcpy(&mask_dbg.s_addr, netmask_bytes, 4);
    printf("Applied via ioctl -> Interface: %s | IP: %s | Mask: %s\n", 
           iface_name, inet_ntoa(ip_dbg), inet_ntoa(mask_dbg));
	#endif
    return 0;
}