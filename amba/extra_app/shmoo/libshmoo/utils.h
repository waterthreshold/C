#ifndef __UTILS__
#define __UTILS__

#define UTILS_BUFF_SIZE		1024
int  get_ip(char *ip, int size);
int  get_mac(char *mac, int size);
int get_hostname(char *hostname);
int get_fwver(char *fwver,int size);
int read_hw_ver ();
#endif