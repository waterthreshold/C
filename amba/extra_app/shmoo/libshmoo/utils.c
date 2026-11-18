#include <net/if.h>
#include <ifaddrs.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <net/if.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>

typedef struct {
	unsigned int val;
	const char brd_ver[8];
}HWID;

const HWID hwid_tbl[]={
	{ 41 , "A1"},
	{ 534 , "B1"},
	{ 913 , "B2"},
	{ 1319 , ""},
	{ 1659 , ""},
	{ 2048 , ""},
	{ 2437 , ""},
	{ 2819 , ""},
	{ 3164 , ""},
	{ 3560 , ""}
};
char hw_ver[32] = {0};


int  get_ip(char *ip, int size)
{
    struct ifaddrs *ifaddr, *ifa;
	// char ip[64};
	int ret = -1;
    getifaddrs(&ifaddr);
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next)
    {
        if (ifa->ifa_addr == NULL) continue;

        if (ifa->ifa_addr->sa_family == AF_INET)
        {
			if (strncmp (ifa->ifa_name, "eth0", strlen (ifa->ifa_name)) == 0) {
				struct sockaddr_in *addr = (struct sockaddr_in *)ifa->ifa_addr;
				struct sockaddr_in *mask = (struct sockaddr_in *)ifa->ifa_netmask;

				strncpy(ip, inet_ntoa(addr->sin_addr),size);
				// strcpy(netmask, inet_ntoa(mask->sin_addr));
				ret=0;
				break; // take first interface
			}
        }
    }
    freeifaddrs(ifaddr);
	return ret;
	// snprintf(response, BUF_SIZE, "IP=%s,NETMASK=%s", ip, netmask);
}


int  get_mac(char *mac, int size)
{
    int sockfd;
    struct ifreq ifr;

    const char *ifname = "eth0";

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0)
    {
        perror("socket");
        return -1;
    }

    memset(&ifr, 0, sizeof(ifr));

    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);

    if (ioctl(sockfd, SIOCGIFHWADDR, &ifr) < 0)
    {
        perror("ioctl");
        close(sockfd);
        return -1;
    }

    // unsigned char *mac =
        // (unsigned char *)ifr.ifr_hwaddr.sa_data;

    snprintf(mac,size,
           "%02X:%02X:%02X:%02X:%02X:%02X",
           (unsigned char *)ifr.ifr_hwaddr.sa_data[0],
           (unsigned char *)ifr.ifr_hwaddr.sa_data[1],
           (unsigned char *)ifr.ifr_hwaddr.sa_data[2],
           (unsigned char *)ifr.ifr_hwaddr.sa_data[3],
           (unsigned char *)ifr.ifr_hwaddr.sa_data[4],
           (unsigned char *)ifr.ifr_hwaddr.sa_data[5]);

    close(sockfd);
    return 0;
	// snprintf(response, BUF_SIZE, "IP=%s,NETMASK=%s", ip, netmask);
}

int get_hostname(char *hostname)
{
	int ret=0;
	if (gethostname(hostname, 1024) != 0)
    {
        perror("gethostname");
        return -1;
    }	
	return ret;
	
}

int get_fwver (char *ver,int size){
	int fd;
	int ret=0;
	char *buffer = (char*) malloc (size);
	if ( (fd=open("/etc/fw_version", O_RDONLY)) < 0 )
	{
		perror ("fw_ver");
		ret = -1;
		goto E_FAILED;
	}
	int n = read(fd,buffer,size);
	memcpy (ver,buffer,n);
	close(fd);
E_FAILED:
	if (buffer) free(buffer);
	
	return ret;	
}

int read_hw_ver (){
	#define MAIN_BOARD_VER_ADC_PATH  "/sys/bus/iio/devices/iio:device0/in_voltage1_raw"
	int fd;
	char buffer[16] = {0};
	int adc_val = -1;
	int i,idx = -1;
	fd = open (MAIN_BOARD_VER_ADC_PATH , O_RDONLY);
	if (fd < 0 ){
		return -1;
	}
	int n = read(fd, buffer,  sizeof(buffer));
	if ( n > 0 ) 
		adc_val = atoi(buffer);
	for (i = 0; i < sizeof(hwid_tbl) / sizeof(HWID) ;i++){
		if (hwid_tbl[i].val > adc_val){
			idx = i;
			idx= (idx -1  < 0) ? 0 : idx-1; 
			if ( strlen (hwid_tbl[idx].brd_ver) > 0 )
			{	
				strncpy (hw_ver,hwid_tbl[idx].brd_ver,strlen (hwid_tbl[idx].brd_ver));
			} 
			else if ( strlen (hwid_tbl[idx].brd_ver) == 0 )
			{
				snprintf( hw_ver,  sizeof(hw_ver), "undefined(%c1)", 'A' + idx);
			}
			
			break;
		}
	}
	close (fd);
	return idx;
}