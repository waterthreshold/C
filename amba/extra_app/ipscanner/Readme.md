# Ambarella CV5 IP Camera Network Protocol Specification

This document outlines the binary UDP packet structures used for communication between the PC client configuration tool and the embedded IP cameras on port `4022`.

---

## 1. PC Client Request Packet (`PCEdit`)
Used by the PC client to either broadcast a **Scan** command or apply a **Setting** update. Total packet size is strictly **74 bytes**.

| Offset / Field | Type / Size | Description / Value |
| :--- | :--- | :--- |
| `header` | `char[6]` | Magic identifier: `"PCEdit"` |
| `type` | `uint8_t` | Command type: `2` = Scan, `1` = Setting |
| `ifname` | `char[4]` | Network interface name: `"eth0"` |
| `ip_addr` | `uint8_t[4]` | Target IPv4 address |
| `mac_addr` | `uint8_t[6]` | Target hardware MAC address |
| `netmask` | `uint8_t[4]` | Subnet Mask |
| `gw_marker` | `char[3]` | Gateway marker: `"\x00GW"` |
| `gateway` | `uint8_t[4]` | Default Gateway IPv4 address |
| `enable_name` | `uint8_t` | Flag to enable hostname change (`1` = enabled) |
| `camera_name` | `char[18]` | Hostname/Camera name (Null-terminated / padded) |
| `padding` | `uint8_t[21]` | Zero-padding buffer (`21 bytes`) |
| `enable_dhcp` | `uint8_t` | Enable DHCP flag (`1` = enabled) |
| `dhcp_flag` | `uint8_t` | Mode flag: `0` = Static IP, `1` = DHCP |

---

## 2. Device Scan Response Packet (`IPCam`)
When the device receives a Scan command (`type = 2`), it responds with its current network and system parameters using the following layout.

| Field | Type / Size | Description / Example |
| :--- | :--- | :--- |
| `camFlag` | `char[5]` | Device identifier: `"IPCam"` |
| `changed` | `unsigned char` | Status flag (`0`) |
| `unknown_name` | `char[4]` | Interface name (`"eth0"`) |
| `ipaddr` | `char[4]` | Current device IPv4 address |
| `hwaddr` | `char[6]` | Hardware MAC address |
| `netmask` | `char[4]` | Current Subnet Mask |
| `reserved` | `unsigned char` | Reserved byte (`0`) |
| `staticreserved` | `char[2]` | Gateway text marker (`"gw"`) |
| `ipaddr2` | `char[4]` | Gateway / Secondary IP reference |
| `reserved_dot` | `char` | Delimiter / Padding byte (`0`) |
| `name` | `char[18]` | Current camera hostname |
| `port1` | `char[5]` | Primary HTTP port (`"80"`) |
| `port2` | `char[5]` | Secondary port (`"0"`) |
| `unknownbyte` | `char` | DHCP state indicator (`0` = Static, `1` = DHCP) |
| `dns1` | `char[4]` | Primary DNS server (e.g., `8.8.8.8`) |
| `dns2` | `char[4]` | Secondary DNS server (e.g., `8.8.8.8`) |
| `i_Protoe` | `char` | Protocol mode (`0`) |
| `i_input_source` | `char` | Input pipeline source (e.g., `0` for larnaca2) |

---

## 3. Implementation Notes
* **Endianness:** Network byte order (Big-Endian) is applied for multi-byte network fields via socket conversion utilities.
* **Alignment:** C-side packet parsers must use strict packing directives (`#pragma pack(1)` or `__attribute__((packed))`) to prevent compiler padding misalignment across the 74-byte structure boundaries.