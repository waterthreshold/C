#ifndef NETLIB_H
#define NETLIB_H

#include <stddef.h> // For size_t

#ifdef __cplusplus
extern "C" {
#endif

#define DEBUG

// Retrieves the IP address (4 raw bytes) for the given interface (e.g., "eth0")
int GetIp(char *p, const char *intface);

// Retrieves the Subnet Mask (4 raw bytes) for the given interface
int GetNetMask(char *p, const char *intface);

// Retrieves the MAC / Hardware address (6 raw bytes) for the given interface
int GetEthrAddr(char *p, const char *intface);

// Retrieves the Default Gateway IP (4 raw bytes) for the given interface
int GetGw(char *p, const char *intface);

// Retrieves the primary DNS server IP (4 raw bytes) from system resolv.conf
int GetDns(char *p, const char *intface, int index);

// Retrieves the system hostname into buffer p up to maxlen
int GetHostName(char *p, size_t maxlen);

// Checks if DHCP is active/enabled (returns 1 if active, 0 otherwise)
int CheckDhcp(const char *intface);
int apply_hostname_confing(const char *name, int len);
int apply_network_interface(const uint8_t *ip, const uint8_t *netmask, const char *iface_name);
#ifdef __cplusplus
}
#endif

#endif // NETLIB_H