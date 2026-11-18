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
#include "netlib.h"


#define MCTESTPORT 			4022
#define IPEDITFLAG 			"PCEdit"
#define IPFLAGLEN 			6
#define NET_INTF			"eth0"
#define MAX_CMD_BUFFERLEN	512
// Define the updated packet structure with packing
typedef struct __attribute__((packed)) {
    char camFlag[5];         // "IPCam"
    unsigned char changed;   // 0
    char unknown_name[4];    // "eth0"
    char ipaddr[4];          // 192.168.7.20
    char hwaddr[6];          // 12:34:56:67:89:12
    char netmask[4];         // 255.255.255.0
    unsigned char reserved;  // 0
    char staticreserved[2];  // "gw"
    char ipaddr2[4];         // 192.168.7.20
	char reserved_dot; 	// 0
    char name[18];           // "test"
    char port1[5];           // "80"
    char port2[5];           // "0"
    char unknownbyte;        // 0 // 0: static 1: dhcp
    char dns1[4];            // 8 8 8 8
    char dns2[4];            // 8 8 8 8
    char i_Protoe;           // 0
    char i_input_source;  // 0: larnaca2 
} DeviceConfigPacket;

#pragma pack(push, 1)

typedef struct {
    char ifname[4];          // 4 bytes: "eth0"
    uint8_t ip_addr[4];      // 4 bytes: Target IP
    uint8_t mac_addr[6];     // 6 bytes: Hardware MAC address
    uint8_t netmask[4];      // 4 bytes: Subnet Mask
    char gw_marker[3];       // 3 bytes: "\x00GW" (Gateway marker)
    uint8_t gateway[4];      // 4 bytes: Gateway IP
    uint8_t enable_name;     // 1 byte:  Enable change Camera name
    char camera_name[18];    // 18 bytes: Camera name
    uint8_t padding[21];     // 21 bytes: Fulfill 21 bytes padding
    uint8_t enable_dhcp;     // 1 byte:  Enable DHCP byte
    uint8_t dhcp_flag;       // 1 byte:  DHCP or Static flag (0 or 1)
} __attribute__((packed)) NetworkConfigPacket;

#pragma pack(pop)

int CheckDhcp(const char *intface) 
{
    char pidpath[64];
    
    // Check common BusyBox udhcpc PID file variations
    snprintf(pidpath, sizeof(pidpath), "/var/run/udhcpc-%s.pid", intface);
    if (access(pidpath, F_OK) == 0) return 1;

    snprintf(pidpath, sizeof(pidpath), "/var/run/udhcpc.%s.pid", intface);
    if (access(pidpath, F_OK) == 0) return 1;

    // Check dhcpcd PID file variation
    snprintf(pidpath, sizeof(pidpath), "/var/run/dhcpcd-%s.pid", intface);
    if (access(pidpath, F_OK) == 0) return 1;

    return 0; // Returns 0 if no active DHCP client lock/PID is found
}

int main() 
{
    int st, sd, i1, i2 = 0;
    struct sockaddr_in sah;
    struct sockaddr_in sap;
    fd_set readfds;
    char cam_recv_buf[1024];
	char cmd_buffer[MAX_CMD_BUFFERLEN]="0";
	
	int sys_ret;
//sock:
    memset((char *)&sah, 0, sizeof(sah));
    sah.sin_family = AF_INET;
    sah.sin_port = htons(MCTESTPORT);
    sah.sin_addr.s_addr = INADDR_ANY;
    
    sd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sd < 0) 
    {
        printf("MCTEST:mc_rx_socket:socket() failed %d\n", errno);
        return sd;
    }
    
    i1 = 1;
    st = setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, (char *)&i1, sizeof(i1));
    if (st < 0) 
    {
        printf("MCTEST:mc_rx_socket:setsockopt( SO_REUSEADDR ) %d\n", errno);
        goto unsock;
    }
    i1 = 1;   
    st = setsockopt(sd, SOL_SOCKET, SO_BROADCAST, (char *)&i1, sizeof(i1));
    if (st < 0) 
    {
        printf("MCTEST:mc_tx_socket:setsockopt( SO_BROADCAST ) %d\n", errno);
    }
    st = bind(sd, (struct sockaddr *)&sah, sizeof(sah));
    if (st < 0)
    {
        printf("MCTEST:mc_rx_socket:bind() failed %d\n", st);
        goto unsock;
    }

    i1 = 1;
    st = setsockopt(sd, IPPROTO_IP, IP_MULTICAST_LOOP, (char *)&i1, sizeof(i1));
    if (st < 0) 
    {
        printf("MCTEST:mc_rx_socket:setsockopt( IP_MULTICAST_LOOP ) %d\n", errno);
    }

    while(1)
    {
        int ret;
        i2++;
        FD_ZERO(&readfds);
        FD_SET(sd, &readfds);
        
        ret = select(sd + 1, &readfds, NULL, NULL, NULL);
    
        if(ret > 0)
        {
            socklen_t addr_len = sizeof(sap);
            st = recvfrom(sd, cam_recv_buf, sizeof(cam_recv_buf) - 1, 0, (struct sockaddr*)&sap, &addr_len);
            
            if (st > 0)
            {
                cam_recv_buf[st] = '\0';
                
                if (memcmp(IPEDITFLAG, &cam_recv_buf[0], IPFLAGLEN) == 0)
                {
					int namelen = strlen (IPEDITFLAG);
					if (cam_recv_buf[namelen] == 0x02) { // broadcast the ip
						char testbuf[512];
						memset(testbuf, 0, sizeof(testbuf));

						DeviceConfigPacket pkt;
						memset(&pkt, 0, sizeof(pkt));

						// Fill structure fields
						memcpy(pkt.camFlag, "IPCam", 5);
						pkt.changed = 0;
						memcpy(pkt.unknown_name, NET_INTF, 4);
						
					   // pkt.ipaddr[0] = 192; pkt.ipaddr[1] = 168; pkt.ipaddr[2] = 7; pkt.ipaddr[3] = 4;
						GetIp(pkt.ipaddr, NET_INTF);
						GetEthrAddr(pkt.hwaddr, NET_INTF);
						GetNetMask(pkt.netmask, NET_INTF);
						// unsigned char mac[6] = {0x12, 0x34, 0x56, 0x67, 0x89, 0x12};
						// memcpy(pkt.hwaddr, mac, 6);
						
						// pkt.netmask[0] = 255; pkt.netmask[1] = 255; pkt.netmask[2] = 255; pkt.netmask[3] = 0;
						
						pkt.reserved = 0;
						memcpy(pkt.staticreserved, "gw", 2);
						GetGw(pkt.ipaddr2, NET_INTF);
						// pkt.ipaddr2[0] = 192; pkt.ipaddr2[1] = 168; pkt.ipaddr2[2] = 7; pkt.ipaddr2[3] = 4;
						pkt.reserved_dot =0;
						// strncpy(pkt.name, "test", sizeof(pkt.name));
						GetHostName(pkt.name, sizeof(pkt.name));
						// Fill new fields
						strncpy(pkt.port1, "80", sizeof(pkt.port1));
						strncpy(pkt.port2, "0", sizeof(pkt.port2));
						pkt.unknownbyte = 0;
						
						// pkt.dns1[0] = 8; pkt.dns1[1] = 8; pkt.dns1[2] = 8; pkt.dns1[3] = 8;
						// pkt.dns2[0] = 8; pkt.dns2[1] = 8; pkt.dns2[2] = 8; pkt.dns2[3] = 8;
						memset (pkt.dns1, 8,sizeof(pkt.dns1));
						memset (pkt.dns2, 8,sizeof(pkt.dns2));
						GetDns(pkt.dns1, NET_INTF,1);
						GetDns(pkt.dns2, NET_INTF,2);
						pkt.i_Protoe = CheckDhcp(NET_INTF);
						pkt.i_input_source = 0 ;
						// int input_source_val = (71 << 8) | 4;
						// memcpy(pkt.i_input_source, &input_source_val, sizeof(input_source_val));

						// Copy structure into the 512-byte testbuf
						memcpy(testbuf, &pkt, sizeof(DeviceConfigPacket));

						// Interface check and transmission
						struct ifreq ifr;
						memset(&ifr, 0, sizeof(ifr));
						strncpy(ifr.ifr_name, NET_INTF, IFNAMSIZ - 1);
						ifr.ifr_addr.sa_family = AF_INET;
											
						if ((ioctl(sd, SIOCGIFFLAGS, &ifr) >= 0) && (ifr.ifr_flags & IFF_UP)) 
						{
							if (setsockopt(sd, SOL_SOCKET, SO_BINDTODEVICE, "eth0", 5) == -1) 
							{
								printf("mctest: setsockopt %s SO_BINDTODEVICE failed\n", "eth0");
							}    
							
							int sendlen = 71;
							// struct sockaddr_in tx_sap = sap;
								struct sockaddr_in tx_sap;
								 memset((char *)&tx_sap, 0, sizeof(tx_sap));
								tx_sap.sin_family = AF_INET;
								tx_sap.sin_port = htons(MCTESTPORT);
								tx_sap.sin_addr.s_addr = 0xffffffff;//INADDR_BROADCAST;
							st = sendto(sd, testbuf, sendlen, 0, (struct sockaddr *)&tx_sap, sizeof(tx_sap));
							if (st != sendlen) 
							{
								printf("MCTEST:mc_tx_socket:sendto failed or incomplete. st=%d, sendlen=%d, errno:%d\n", st, sendlen, errno);
							}
							#ifdef DEBUG
							else {
								printf ("ipscanner gotcha!!\n");
							}
							#endif
						}
					} else if (cam_recv_buf[namelen] == 0x01) {  // setting 
						NetworkConfigPacket *config_pkt = (NetworkConfigPacket *)(cam_recv_buf + namelen + 1);
						int dhcp_setting = (int)config_pkt->dhcp_flag;
						int enable_name_flag = (int)config_pkt->enable_name;
						if ( enable_name_flag == 1 )
							apply_hostname_confing(config_pkt->camera_name, sizeof(config_pkt->camera_name));
						
						if (dhcp_setting == 1 ){
							if (CheckDhcp(NET_INTF) == 0 ){
								snprintf(cmd_buffer, sizeof(cmd_buffer), "killall udhcpc; udhcpc -i %.4s -p /var/run/udhcpc1.pid -s /usr/share/udhcpc/default.script &", NET_INTF);
								sys_ret = system(cmd_buffer); 
								memset (cmd_buffer, 0 ,MAX_CMD_BUFFERLEN );
							}
						} else {
							snprintf(cmd_buffer, sizeof(cmd_buffer), "killall udhcpc");
							sys_ret = system(cmd_buffer);
							memset (cmd_buffer, 0 ,MAX_CMD_BUFFERLEN );
							apply_network_interface(config_pkt->ip_addr, config_pkt->netmask , NET_INTF);
						}
					}
                }
            }
        }
    }

unsock:
    if (sd >= 0)
    {
        close(sd);
    }
    return sd;
}
