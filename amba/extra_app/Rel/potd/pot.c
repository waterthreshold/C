/************************************************
 * functions implemented in POT flash partition *
 *        Delta Networks Ltd. (R) 2022          *
 ************************************************/

/***
 * NETGEAR SPEC Rev 16 page 315 
 * ------------------------------------------------------------------------------------
 * In order to minimize the risk of corrupting the flash, a simple bit write operation (not erase / write)
 * should be used to change the POT value counter. For example, if the original state of the flash is all
 * zeroes, whenever we increment the POT counter / value, we simply set the lowest bit to 1. The next
 * increment will set the next bit to 1. Therefore, we will need 4320 bits or 540 bytes to store up to three
 * days of POT value. Since we are not using the complete erase and write operation, there is less chance
 * of flash corruption.
 * ------------------------------------------------------------------------------------
 *
 * The DUT's original state of MTD flash is all ones: 0xFFFFFFFF, 0xFFFFFFFF ....
 ***/

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <sys/un.h>
#include <sys/time.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <errno.h>

#include "common.h"
#if 0

#include "ambitCfg.h"
#endif

#define LOCK_FILE "/tmp/potd.pid"

/* potd: functions */
 static int lock_fd = -1;

 
 // Function to ensure single instance
 int check_single_instance(const char *lockfile_path) {
	 // 1. Open or create the lock file
	 lock_fd = open(lockfile_path, O_RDWR | O_CREAT, 0640);
	 if (fd < 0) {
		 perror("Could not open lock file");
		 return -1;
	 }
 
	 // 2. Try to acquire an exclusive, non-blocking lock
	 if (flock(lock_fd, LOCK_EX | LOCK_NB) < 0) {
		 if (errno == EWOULDBLOCK) {
			 fprintf(stderr, "Error: Another instance of this daemon is already running.\n");
		 } else {
			 perror("Error locking file");
		 }
		 close(lock_fd);
		 return -1; // Already running or error
	 }
 
	 // 3. Optional: Write current PID to the lock file for reference
	 if (ftruncate(lock_fd, 0) < 0) {
		 perror("Could not truncate lock file");
	 }
	 
	 char pid_str[32];
	 snprintf(pid_str, sizeof(pid_str), "%d\n", getpid());
	 if (write(lock_fd, pid_str, strlen(pid_str)) < 0) {
		 perror("Could not write PID to lock file");
	 }
 
	 // Note: Do NOT close(fd) here! 
	 // Keeping the file descriptor open keeps the lock active until the program exits.
	 return 0;
 }
 
 
 static int  set_potval(int pot_value)
{
	int n;
	unsigned char byte_value;
	FILE *fp = NULL;
	
	/* sanity check */
    if (pot_value <= 0) {
        printf("POT: wrong pot_value %d\n", pot_value);
        return -1;
    }
    
  

	fp = fopen(POT_MTD, "r+");
	if(fp == NULL )
	{
		printf("POT: failed to open %s\n", POT_MTD);
		return -1;
	}
	
	fseek (fp, SECTOR_FLAG_LEN + (pot_value-1)/8, SEEK_SET);

    n = (pot_value-1) % 8;
    
    byte_value = (unsigned char)((1<<(7-n)) - 1);
    /* printf("pot_value = %08x, byte = %02x, n = %d\n", 
                pot_value, byte_value, n); */ 
	#if 1 
	char tmp[32];
	snprintf (tmp,sizeof(tmp),"%d",pot_value);
	//acosNvramConfig_set("potValue",tmp);
	#endif
	if( sizeof(byte_value) != fwrite(&byte_value, 1, sizeof(byte_value), fp))
	{
		fclose(fp);
		return -1;
	}
    fsync(fp); 
    fclose(fp);
	
	//return 0;
}
#if 1
static int pot_write (char *buf, unsigned long len)
{
    FILE *fp = NULL;

	fp = fopen(POT_MTD, "w");
	if(fp == NULL )
	{
		printf("can't create POT file %s\n", POT_MTD);
		return -1;
	}
	
	if( len != fwrite(buf, 1, len, fp))
	{
		fclose(fp);
		return -1;
	}
	
	/* to ensure data are written to flash */
    fsync(fp);
    fclose(fp);
	
	return 0;
}


int potFlash_Erase (int signatureCheck)
{
    unsigned char buf[POT_SPACE]; /* a 64k buffer */
    char signature[7];
    int ret;
    /* foxconn modified start, zacker, 03/11/2011 */

    memset (buf, 0xFF, sizeof (buf));

    memcpy (buf, SECTOR_FLAG, SECTOR_FLAG_LEN);

    
    /* set nvram value to 0 */
    //acosNvramConfig_set ("potValue", "0");

    /* foxconn added start, zacker, 05/21/2010, @ntp_record */
#ifdef NTP_SYNC_RECORD
    acosNvramConfig_set ("ntp_sync_time", "");
#endif
    /* foxconn added end, zacker, 05/21/2010, @ntp_record */

    /* foxconn added start, zacker, 06/22/2010, @wl_access_record */
#ifdef WL_ACCESS_RECORD
    acosNvramConfig_set ("access_mac_record", "");
#endif
    /* foxconn added end, zacker, 06/22/2010, @wl_access_record */


    ret = pot_write (buf, sizeof(buf));
    if (ret < 0)
    {
        if (!signatureCheck)
        {
            unlink(POT_MTD);
            ret = pot_write (buf, sizeof(buf));
        }
    }
    if (ret < 0)
        printf("POT: erase pot sector failed.\n");


  

    return 0;
}

static int abPotErase (void)
{
    int ret = 0;

    ret = potFlash_Erase (1);
    if (ret)
        printf ("Erase failed.\n");
    else
        printf ("Erase done.\n");
    return ret;
}
#endif
static void update_to_file(int potval)
{
	FILE *fp;
	if (POT_MAX_VALUE < 0 ){
		goto L_update;
	}
	if (potval > POT_MAX_VALUE)
		potval = POT_MAX_VALUE;

L_update:

	fp = fopen(POT_FILENAME, "w");
	if (fp == NULL) {
		fprintf(stderr, "Can't open " POT_FILENAME "!\n");
		return;
	}
	fprintf(fp, "%d", potval);

	fclose(fp);
}

static void set_page_data(int potval, unsigned char *buf)
{
	unsigned int word, *wordp;

	wordp = (unsigned int *)buf;
	word = potval;
	wordp[0] = word;

}

/**
 * Reads a file and checks if its content is a valid number.
 * 
 * @param filename The path to the file.
 * @param out_num Pointer to store the parsed number if successful.
 * @return 1 if successful and valid, 0 otherwise.
 */
int read_number_from_file(const char *filename, int *out_num) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        return 0; // Failed to open file
    }

    char buffer[256];
    if (fgets(buffer, sizeof(buffer), file) == NULL) {
        fclose(file);
        return 0; // File is empty or read error
    }
    fclose(file);

    // Remove trailing newline or carriage return characters
    buffer[strcspn(buffer, "\r\n")] = '\0';

    // Trim leading whitespace
    char *start = buffer;
    while (*start != '\0' && isspace((unsigned char)*start)) {
        start++;
    }

    // If string was only whitespace
    if (*start == '\0') {
        return 0;
    }

    // Parse string to double using strtod
    char *endptr;
    errno = 0;
    int val = strtoul(start, &endptr,10);

    // Check if conversion failed or if there are leftover non-whitespace characters
    while (*endptr != '\0' && isspace((unsigned char)*endptr)) {
        endptr++;
    }

    if (errno != 0 || endptr == start || *endptr != '\0') {
        return 0; // Not a valid number
    }

    *out_num = val;
    return 1; // Success
}

void cleanup() {    
	if (lock_fd != -1) {        
		close(lock_fd); // Releases the lock
		lock_fd = -1;    
	}
	// Delete the lock file from disk
	unlink(LOCK_FILE);
}

void handle_signal(int sig) {  
	// Calling exit() will automatically trigger functions registered with atexit()
	exit(EXIT_SUCCESS);
}

int pot_func(int argc, char **argv)
{
	int devfd;
	int pot_value;
	struct timeval timo;
	unsigned int word_value;
	unsigned char buf[POT_SPACE],*wordp;
	//struct mtd_info_user mtdInfo;
	//struct erase_info_user mtdEraseInfo;
	int offset=0, i,j;
	unsigned char byte;
	 int val = 0;
	fprintf(stderr, "POT is Running...\n");
#if 1
	if (argc ==2 ) {
		if (strcmp (argv [1] , "erase")==0) {
			abPotErase();
			printf("Erase Done!!\n");
			return 0;
		}
	}
#endif
	atexit(cleanup); // Called on normal exit()   
	signal(SIGINT, handle_signal);   // Handle Ctrl+C    
	signal(SIGTERM, handle_signal);  // Handle standard 'kill <PID>'
	if (check_single_instance(LOCK_FILE) != 0)
	{        
		exit(EXIT_FAILURE);
	}
	devfd = open(POT_MTD, O_RDWR | O_SYNC);
	if (devfd < 0) {
		dfp("Can't open POT mtd - %s\n", POT_MTD);
		return -1;
	}
	read(devfd, buf, SECTOR_FLAG);
	printf ("buf=%s\n",buf);
	if (0 != strncmp (buf, SECTOR_FLAG, 6)) {
        printf ("POT signature check failed.\n");
        return -1;
    }
    
	/* locate to the last page which have the values */
#if 0	
	for (i=0; i < POT_SPACE; i++) {
		lseek(devfd, offset, SEEK_SET);
		read(devfd, buf, sizeof(buf));
		wordp = (unsigned int *)buf;
		word_value = wordp[0];
		if (word_value == 0xFFFFFFFF)
			break;
		offset += sizeof(buf);
	}
	
	if (offset == 0)
		lseek(devfd, MAX_BUFFSZ, SEEK_SET);
	else
		lseek(devfd, offset-NAND_FLASH_PAGESIZE, SEEK_SET);

	/**
	 * count the number of word (4 bytes), not 0x00000000 at the head, and read the
	 * first word which isn't ZERO.
	 */
	 
	read(devfd, buf, sizeof(buf));
	wordp = buf+6;
	word_value = wordp[0];
	if (word_value == 0xFFFFFFFF)
		word_value = 0;
	else if (offset == 0) {
		/*read pot value from another block */
		set_page_data(word_value, buf);
		lseek(devfd, 0, SEEK_SET);
		write(devfd, buf, sizeof(buf));
		offset += NAND_FLASH_PAGESIZE;
	}

	pot_value = word_value;
	update_to_file(pot_value < POT_MAX_VALUE ? pot_value : POT_MAX_VALUE);
	dfp ("word_value=%d pot_value=%d \n",word_value,pot_value);
	if (pot_value >= POT_MAX_VALUE)
		goto fin;
	
	/**memset(&mtdInfo, 0x00, sizeof(struct mtd_info_user));
	memset(&mtdEraseInfo, 0x00, sizeof(struct erase_info_user));
	if (ioctl(devfd, MEMGETINFO, &mtdInfo)) {
		dfp("can't get mtd device info from %s\n", POT_MTD);
		goto fin;
	}*/
	#endif
	 //base = buf + SECTOR_FLAG_LEN;
    offset += SECTOR_FLAG_LEN;
	
    /* search for the first none-zero bit */
    for (i = 0; i < POT_UPPER_BYTE_VALUE; i++)  {
        if ( 0x00 != *(buf + i +offset))
            break;
    }

    if (i >= POT_UPPER_BYTE_VALUE) {
        val = POT_UPPER_BYTE_VALUE*8; /* all 0s */
    } else {
        byte = *(buf + i +offset);

        /* XXX big endian */
        for (j = 0; j < 8; j++) {
            if (byte & (1 << (7-j)))
                break;
        }
        val = 8*i + j;
    }
	printf ("potd start val =%d\n",val);
	pot_value = val;
	read_number_from_file (POT_FILENAME,&pot_value);
	for (;;) {
		timo.tv_sec = POT_RESOLUTION  * 60;
		timo.tv_usec = 1;
		select(1, NULL, NULL, NULL, &timo);

		/* need verify the result of read & write operation ?_? */
		
		//if (offset == NAND_FLASH_BLOCKSIZE) {
		//	offset = 0;
			//  store the next pot value to another block 
			/*mtdEraseInfo.start = NAND_FLASH_BLOCKSIZE;
			mtdEraseInfo.length = mtdInfo.erasesize;
			if (ioctl(devfd, MEMERASE, &mtdEraseInfo)) {
				dfp("Failed to erase block on %s from 0x%08x\n", POT_MTD, mtdEraseInfo.start);
				goto fin;
			}*/
			//set_page_data(pot_value+1, buf);
			//lseek(devfd, NAND_FLASH_BLOCKSIZE, SEEK_SET);
			//write(devfd, buf, sizeof(buf));

			/*mtdEraseInfo.start = 0;
			mtdEraseInfo.length = mtdInfo.erasesize;
			if (ioctl(devfd, MEMERASE, &mtdEraseInfo)) {
				dfp("Failed to erase block on %s from 0x%08x\n", POT_MTD, mtdEraseInfo.start);
				goto fin;
			}*/
		//}
		
		pot_value++;
		if (POT_MAX_VALUE < 0 )
			goto L2;
		else if (pot_value >= POT_MAX_VALUE)
			goto fin;
L2:
		update_to_file(pot_value);
		//set_page_data(pot_value, buf);
		set_potval(pot_value);
		//printf ("pot_value=%d\n",pot_value);
		//lseek(devfd, offset, SEEK_SET);
		//write(devfd, buf, sizeof(buf));
		//offset += NAND_FLASH_PAGESIZE;
	}

fin:
	update_to_file(pot_value);
	fprintf(stderr, "POT is Finished!!!\n");

	close(devfd);
	return 0;
}

 

#if 0
/* potval: functions */
static void set_potval(char *value)
{
	int devfd;
	int pot_value, data;
	unsigned char buf[NAND_FLASH_PAGESIZE];
	struct mtd_info_user mtdInfo;
	struct erase_info_user mtdEraseInfo;
	int page_num, offset = 0, i;

	pot_value = atoi(value);
	if (pot_value < 0 || pot_value > POT_MAX_VALUE)
		return;

	/* stop the POT Demo firstly. */
	system("/usr/bin/killall potd 2> /dev/null");

	/****************************************/
	devfd = open(POT_MTD,O_RDWR|O_SYNC);
	if (devfd < 0)
		goto start;

	/*memset(&mtdInfo, 0x00, sizeof(struct mtd_info_user));
	memset(&mtdEraseInfo, 0x00, sizeof(struct erase_info_user));
	if (ioctl(devfd, MEMGETINFO, &mtdInfo)) {
		dfp("can't get mtd device info from %s\n", POT_MTD);
		goto start;
	}
	mtdEraseInfo.start = 0;
	mtdEraseInfo.length = mtdInfo.erasesize;
	if (ioctl(devfd, MEMERASE, &mtdEraseInfo)) {
		dfp("Failed to erase block on %s from 0x%08x\n", POT_MTD, mtdEraseInfo.start);
		goto start;
	}

	mtdEraseInfo.start = NAND_FLASH_BLOCKSIZE;
	mtdEraseInfo.length = mtdInfo.erasesize;
	if (ioctl(devfd, MEMERASE, &mtdEraseInfo)) {
		dfp("Failed to erase block on %s from 0x%08x\n", POT_MTD, mtdEraseInfo.start);
		goto start;
	}

	mtdEraseInfo.start = FIRST_NTP_TIME_OFFSET;
	mtdEraseInfo.length = mtdInfo.erasesize;
	if (ioctl(devfd, MEMERASE, &mtdEraseInfo)) {
		dfp("Failed to erase block on %s from 0x%08x\n", POT_MTD, mtdEraseInfo.start);
		goto start;
	}*/

	if (pot_value == 0)
		goto start;
#if 0
	page_num = pot_value % (NAND_FLASH_BLOCKSIZE/NAND_FLASH_PAGESIZE);
	if (page_num == 0)
		page_num = (NAND_FLASH_BLOCKSIZE/NAND_FLASH_PAGESIZE);
#endif

	for (i=page_num; i>0; i--) {
		data = pot_value - i + 1;
		set_page_data(data, buf);
		lseek(devfd, offset, SEEK_SET);
		write(devfd, buf, sizeof(buf));
		offset += NAND_FLASH_PAGESIZE;
	}

start:
	close(devfd);
	system("/usr/sbin/potd");
}
#endif
time_t get_ntpsynctime(void)
{
	time_t ntp = 0;
	int fd = 0;

	fd = open(POT_MTD, O_RDWR | O_SYNC);
	if (0 > fd) {
		dfp("can't open mtd device - %s\n", POT_MTD);
		ntp = 0xffffffff;
	} else {
		lseek(fd, NTP_RECORD_OFFSET, SEEK_SET);
		read(fd, &ntp, sizeof(ntp));
		close(fd);
	}
	return ntp;
}

void get_stamac(unsigned char* mac)
{
	int fd = 0;

	if (!mac)
		return;

	fd = open(POT_MTD, O_RDWR | O_SYNC);
	if (0 > fd) {
		dfp("can't open mtd device - %s\n", POT_MTD);
		memset(mac, 0xff, 6);
	} else {
		lseek(fd, FIRST_WIFISTATION_MAC_OFFSET, SEEK_SET);
		read(fd, mac, 6);
		close(fd);
	}
}
/***
 * NETGEAR SPEC Rev 16 page 315 
***/

int potval_func(int argc, char **argv)
{
	FILE *fp;
	fd_set readable;
	int r, listen_fd, conn_fd;
	char recvbuf[128], potval[128];
	struct sockaddr_in addr;
	time_t ntptime;
	char strtime[64] = {0};
	unsigned char mac[6];
	const unsigned char nomac[6] = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
	char timezone[64];
	char tz_env[64];

	listen_fd = socket(AF_INET, SOCK_STREAM, 0);
	if (listen_fd < 0) {
		printf("error socket");
		return -1;
	}

	fcntl(listen_fd, F_SETFD, 1);
	memset(&addr, 0, sizeof(struct sockaddr_in));
	addr.sin_family = AF_INET;
	addr.sin_port   = htons(POT_PORT);
	addr.sin_addr.s_addr = htonl(INADDR_ANY);

	if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0 ||
	    listen(listen_fd, 10) < 0) {
		printf("Can't bind the POT socket");
		close(listen_fd);
		return -1;
	}

	fprintf(stderr, "potval: The POT-(Get/Set) Demo is Running ...\n");

	for (;;) {
		FD_ZERO(&readable);
		FD_SET(listen_fd, &readable);

		if (select(listen_fd + 1, &readable, NULL, NULL, NULL) < 1 ||
		    (conn_fd = accept(listen_fd, NULL, NULL)) < 0)
			continue;

		memset(potval, 0x00, sizeof(potval));
		memset(strtime, 0x00, sizeof(strtime));
		if ((fp = fopen(POT_FILENAME, "r")) == NULL)
			goto cont; /*must be modify*/
		if (!fgets(potval, sizeof(potval), fp))
			potval[0] = '\0';
		fclose(fp);
		strcat(potval, "NTP");
		ntptime = get_ntpsynctime();
		if (0xffffffff == ntptime) {
			strcpy(strtime, "00-00-00");
		} else {
			memset(timezone, 0, sizeof(timezone));
			//strcpy(timezone, acosNvramConfig_get("time_zone"));
			sprintf(tz_env, "TZ=%s", timezone);
			putenv(tz_env);
			printf("Current NTP time_zone = %s \n",timezone);
			strftime(strtime, sizeof(strtime), "%T, %b %d, %Y", localtime(&ntptime));

		}
		strcat(potval, strtime);

		get_stamac(mac);
		if(!memcmp(nomac, mac, 6))
			memset(mac, 0, 6);
		sprintf(potval + strlen(potval), "MAC%02x-%02x-%02x-%02x-%02x-%02x", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
		printf ("potval=%s",potval);
		send(conn_fd, potval, strlen(potval), 0);
		r = recv(conn_fd, recvbuf, sizeof(recvbuf) - 1, 0);
		if (r < 1)
			goto cont;
		recvbuf[r] = '\0';
		/* printf("POT Recv'd Data : %s\n", recvbuf); */
		if (strcmp(recvbuf, "get"))
			set_potval(recvbuf);
	cont:
		close(conn_fd);
	}

	shutdown(listen_fd, 2);
	close(listen_fd);
	return 0;
}

int main(int argc, char *argv[])
{
	daemon(1, 1);

	if (strstr(argv[0], "ntpst") != NULL)
		return ntpst_func(argc, argv);
	else if (strstr(argv[0], "stamac") != NULL)
		return stamac_func(argc, argv);
	else if (strstr(argv[0], "potval") != NULL)
		return potval_func(argc, argv);
	else if (strstr(argv[0], "potd") != NULL)
		return pot_func(argc, argv);
	else
		dfp("command name is wrong!\n");

	return -1;
}
