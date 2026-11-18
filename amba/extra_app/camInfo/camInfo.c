#include <stdio.h>
#include <dirent.h>
#include <ctype.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <termios.h>
#include <linux/module.h> 

#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

#define MAX_PROCESS_NAME_LEN 256
#define MAX_BUFFER_STRING_LEN	1024
#define MAX_PATH_LEN	1024

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
char sensor_name[32] = {0};
#if 1 
// int i2c_read()
int get_sensor_name(){
	int file;
    int adapter_nr = 0;
    int addr = 0x36;  // device address

    char filename[20];
    sprintf(filename, "/dev/i2c-%d", adapter_nr);

    file = open(filename, O_RDWR);
    if (file < 0) {
        perror("open");
        return 1;
    }

    if (ioctl(file, I2C_SLAVE, addr) < 0) {
        perror("ioctl");
        return 1;
    }
	unsigned char standby_reg[3] = { 0x30 , 0x00 ,0x00};
    unsigned char reg[2] = {0x4D, 0x12};
	unsigned char reg1[2] = {0x4D, 0x13};
	unsigned char standby_data[1];
    unsigned char data[1];
	unsigned char data1[1];
    
	// Write register address
    if (write(file, standby_reg, 2) != 2) {
        perror("write reg");
        return 1;
    }

    // Read data
    if (read(file, standby_data, 1) != 1) {
        perror("read");
        return 1;
    }
	// int ret_standbymode  = atoi (standby_data);
	if (standby_data[0] == 0x1  )
	{
		if (write(file, standby_reg, 3) != 3) {
			perror("write reg");
			return 1;
		}
		// write(file, 0x01, 1);
		usleep(500000);
	}
	
	// Write register address
    if (write(file, reg, 2) != 2) {
        perror("write reg");
        return 1;
    }

    // Read data
    if (read(file, data, 1) != 1) {
        perror("read");
        return 1;
    }
	if (write(file, reg1, 2) != 2) {
        perror("write reg");
        return 1;
    }

    // Read data
    if (read(file, data1, 1) != 1) {
        perror("read");
        return 1;
    }
    printf("Data:  0x%02X 0x%02X\n",  data1[0] ,data[0]);

    close(file);
    return 0;
}

#endif
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

int is_process_running_by_name(const char *name)
{
    DIR *dir = opendir("/proc");
    if (!dir) return 0;

    struct dirent *ent;
    char path[256], cmdline[MAX_PROCESS_NAME_LEN];
    FILE *fp;

    while ((ent = readdir(dir)) != NULL)
    {
        if (!isdigit(ent->d_name[0]))
            continue;

        snprintf(path, sizeof(path), "/proc/%s/comm", ent->d_name);
        fp = fopen(path, "r");
        if (fp)
        {
            fgets(cmdline, sizeof(cmdline), fp);
            cmdline[strcspn(cmdline, "\n")] = 0;
            fclose(fp);

            if (strncmp(cmdline, name,15) == 0)
            {
				// printf ("hit %s\n",name);
                closedir(dir);
                return 1;
            }
        }
    }

    closedir(dir);
    return 0;
}

char* get_projectcode(){
	int fd;
	static char buf [MAX_BUFFER_STRING_LEN]={0};
	if (strlen (buf) > 0 ){
		return buf;
	}
	if ( ( fd = open ("/etc/project_code",O_RDONLY)) > 0 ){
		ssize_t n = read(fd, buf, MAX_BUFFER_STRING_LEN);
		if ( n > 0 ){
			return buf;
		}
	} 
	
	return "None";
}

char* get_fwversion(){
	int fd;
	static char buf [MAX_BUFFER_STRING_LEN]={0};
	if (strlen (buf) > 0 ){
		return buf;
	}
	if ( ( fd = open ("/etc/fw_version",O_RDONLY)) > 0 ){
		ssize_t n = read(fd, buf, MAX_BUFFER_STRING_LEN);
		if ( n > 0 ){
			return buf;
		}
	} 
	
	return "None";
}

int is_streaming_start(){
	const char process_checklist[][MAX_PROCESS_NAME_LEN] = { "rtsp_server" , "test_aaa_service" };
	int i;
	// printf ("%d\n",sizeof(process_checklist)/ sizeof(process_checklist[0]));
	for (i = 0 ; i < sizeof(process_checklist)/ sizeof(process_checklist[0]) ; i++) {
		int ret = is_process_running_by_name (process_checklist[i]);
		// printf ("ret=%d\n");
		if ( ret == 0)
			return 0;
	}
	return 1;
}

int  mcu_version(/*int serial*/){
	const int serial[]={3,4};
	char *portname= (char *) malloc(MAX_PATH_LEN);
	#define MCU_FW_VERSION	(0x80180000)
	int i;
	printf ("Totaol: %d\n",sizeof (serial) / sizeof(int));
    // 1. Open serial port
	for (i=0 ;i< sizeof (serial) / sizeof(int); i++){
		memset(portname, 0 , MAX_PATH_LEN);
		snprintf (portname,MAX_PATH_LEN,"/dev/ttyS%d",serial[i]);
		int fd = open(portname, O_RDWR | O_NOCTTY | O_SYNC);
		if (fd < 0) {
			perror("open");
			return 1;
		}

		// 2. Get current port settings
		struct termios tty;
		if (tcgetattr(fd, &tty) != 0) {
			perror("tcgetattr");
			close(fd);
			return 1;
		}

		// 3. Configure port
		cfsetospeed(&tty, B115200);
		cfsetispeed(&tty, B115200);

		// 8 data bits, no parity, 1 stop bit (8N1)
		tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
		tty.c_cflag &= ~(PARENB | PARODD); // no parity
		tty.c_cflag &= ~CSTOPB;            // 1 stop bit
		tty.c_cflag &= ~CRTSCTS;           // no flow control
		tty.c_cflag |= (CLOCAL | CREAD);   // enable receiver

		// raw input (no canonical mode, no echo)
		tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
		tty.c_iflag &= ~(IXON | IXOFF | IXANY); // no software flow control
		tty.c_iflag &= ~(INLCR | ICRNL | IGNCR);
		tty.c_oflag &= ~OPOST; // raw output

		// read timeout: 1s
		tty.c_cc[VMIN]  = 0;
		tty.c_cc[VTIME] = 10;

		// 4. Apply settings
		if (tcsetattr(fd, TCSANOW, &tty) != 0) {
			perror("tcsetattr");
			close(fd);
			return 1;
		}

		// 5. Write data
		char msg[MAX_BUFFER_STRING_LEN] = {0};
		snprintf (msg,MAX_BUFFER_STRING_LEN,"CMD:%u~END",MCU_FW_VERSION);
		write(fd, msg, strlen(msg));

		// 6. Read response
		char buf[100]={0};
		int n = read(fd, buf, sizeof(buf));
		if (n > 0) {
			buf[n] = '\0';
			printf("MCU %d (%s) Received: %s", (i+1),portname, buf);
		}
		tcflush(fd,TCIOFLUSH);
		close(fd);
	}
	if (portname)
		free (portname);
    return 0;
}

int is_running_yolov3()
{
	// if (find_module("cavalry")) {
		// pr_info("module is loaded\n");
	FILE *fp=NULL;
	char buffer [MAX_BUFFER_STRING_LEN] = {0}; 
	if ( (fp = popen("lsmod | grep cavalry", "r") ) != NULL ) {
		fread (buffer, MAX_BUFFER_STRING_LEN ,1 , fp );
		char* ret = strstr(buffer,"cavalry");
		return (ret?1:0); 
	}
	return 0;
	
}
int main (int argc, char *argv[]) {
	
	const char stresstest_cmd [][MAX_PROCESS_NAME_LEN]= { "cpu_full_load", "memtester-arm", "bandwidth-arm-thread"};
	int i;
	
	char *s=get_fwversion();
	printf ("fw version: %s",s);
	s=get_projectcode();
	printf ("Project code: %s\n",s);
	printf ("streaming detect: %s\n",is_streaming_start()?"Y":"N");
	printf ("cavalry detect: %s\n",is_running_yolov3()?"Y":"N");
	printf ("Stress test command running: ");
	int process_found = 0 ; 
	for ( i=0 ;i < sizeof(stresstest_cmd) / sizeof (stresstest_cmd[0]); i++){
		if (is_process_running_by_name(stresstest_cmd[i])){
			process_found=1;
			printf ("%s,",stresstest_cmd[i]);
		}
	}
	if (process_found == 0 )
		printf ("None\n");
	else
		printf ("\n");
	printf("MCU:\n");mcu_version();
	
	read_hw_ver() ? printf ("HW ver: %s\n",hw_ver) : printf ("error\n");
	get_sensor_name();
	return 0;
}


