#ifndef __CONFIG_H_
#define __CONFIG_H_

#define POT_MTD			"/root/POT"
#define POT_FILENAME		"/root/pot_value"




#define POT_MAX_VALUE	(-1)		/* 4320 minutes */
#define POT_RESOLUTION	1		/* minute */
#define POT_PORT	3333		/* potval listen this port */
#if 0
#define NAND_FLASH_BLOCKSIZE	(128 * 1024)	/* bytes, 128KB */
#define NAND_FLASH_PAGESIZE	(2 * 1024)	/* bytes, 2KB */
#endif

#define NTP_RECORD_OFFSET    (0x800)
#define SECTOR_FLAG_LEN 6       /* strlen("POTTOP") = 6 */

#define FIRST_WIFISTATION_MAC_OFFSET	(4 + NTP_RECORD_OFFSET)

#define FIRST_NTP_TIME_OFFSET	(FIRST_WIFISTATION_MAC_OFFSET + 16)

#define POT_SPACE		0x10000


#define MAX_BUFFSZ 1024




#define SECTOR_FLAG "POTTOP"
#define POT_UPPER_BYTE_VALUE (NTP_RECORD_OFFSET - SECTOR_FLAG_LEN)

#endif
