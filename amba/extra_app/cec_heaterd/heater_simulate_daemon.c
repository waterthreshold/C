#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <signal.h>
#include <syslog.h>

#define TEMP_PATH "/sys/class/hwmon/hwmon0/temp1_input"
#define TEMP2_PATH "/sys/bus/iio/devices/iio:device0/in_voltage2_raw"
#define GPIO_PATH "/sys/class/gpio/gpio61/value"
#define CHECK_INTERVAL 5
#define THRESHOLD -15000   // -15°C
#define LOWERTHRESHOLD  -10000

static int running = 1;

void handle_signal(int sig)
{
    running = 0;
}

int read_temperature()
{
    int fd = open(TEMP_PATH, O_RDONLY);
	int fd2 = open(TEMP2_PATH, O_RDONLY);
    if (fd < 0) return 0;
	if (fd2 < 0 ) return 0;

    char buf[32] = {0}, buf2[32]={0};
    read(fd, buf, sizeof(buf));
    read(fd2, buf2, sizeof(buf2));
	int adc =  atoi (buf2);
	if (adc < 308 ) {
		printf("Assuming heater was auto start %d!!\n",adc);
		syslog(LOG_INFO, "Assuming heater was auto start %d!!",adc);
		
	}
	close(fd);
	close (fd2);
    return atoi(buf);
}

int read_heater(){
	int fd = open(GPIO_PATH, O_RDONLY);
	char buf[8]={0};
    int on = -1;
	
	if (fd < 0) return -1 ;

    read(fd, buf, 1);
	on = atoi (buf);
    close(fd);
	return on;
}

void set_heater(int on)
{
	int heater_en = read_heater();
	if (heater_en < 0) return ;
	if (heater_en == on )
		return;
    int fd = open(GPIO_PATH, O_WRONLY);
    if (fd < 0) return;

    write(fd, on ? "1" : "0", 1);
	printf ("Set Heater %s\n",on?"on":"off");
	syslog(LOG_INFO, "Set Heater %s",on?"on":"off");
    close(fd);
}

void initialize_gpio(){
	int fd = open("/sys/class/gpio/export", O_WRONLY);
    if (fd < 0) return;
	write(fd, "61", 2);
	close(fd);
	fd = open("/sys/class/gpio/gpio61/direction", O_WRONLY);
    if (fd < 0) return;
	write(fd, "out", 3);
	close (fd);
}

int main()
{
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);
	printf ("Heater Program Start\n");
	syslog(LOG_INFO, "Heater Program Start");
	initialize_gpio();
	openlog("tempd", LOG_PID | LOG_CONS, LOG_DAEMON);
	printf ("Heater init %s\n",read_heater()?"on":"off") ;
    syslog(LOG_INFO, "Heater init %s",read_heater()?"on":"off");
    if (daemon(0, 0) < 0)
    {
        perror("daemon");
        exit(EXIT_FAILURE);
    }

    int heater_on = 0;
	

    while (running)
    {
        int temp = read_temperature();

        if (temp < THRESHOLD)
        {
            set_heater(1);
            heater_on = 1;
        } 
		else if ( temp > LOWERTHRESHOLD){
			set_heater(0);
            heater_on = 0;
		}
        else
        {
            set_heater(0);
            heater_on = 0;
        }

        sleep(CHECK_INTERVAL);
    }

    set_heater(0);
    return 0;
}
