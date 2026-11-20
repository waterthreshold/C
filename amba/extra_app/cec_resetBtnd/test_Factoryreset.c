#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <linux/input.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

#define KEY_FACTORYRESET 28  //  Reset button code
#define MAX_WAIT_TIME 10   // Seconds
#define TRIGGER_WAIT_TIME 3
 
enum RESETBTN_RESULT {
	RESULT_UNKNOWN = -2,
	RESULT_FAILED,
	RESULT_SUCCESS,
	RESULT_TIMEOUT
};


time_t current_time(){
	time_t current;	
	time(&current);
	return current;
}

int g_FactoryPressed=0;
int g_Success=RESULT_UNKNOWN;

int main(int argc, char *argv[]) {
	int index = 1;
	if ( argc == 2) {
		index = atoi(argv[1]);
	} 
	
   	char device[128] =  {0};// Adjust to your keyboard device
	snprintf (device, sizeof(device), "/dev/input/event%d", index);
	time_t start,press_time;
	struct timeval timeout;
	timeout.tv_sec 	=1;
	timeout.tv_usec = 0;
	fd_set fds;
	FD_ZERO(&fds);
	//printf ("Please push the factory reset button in 10 seconds...\n");
	printf ("Detect Reset Button start!!\n");
	

    int fd = open(device, O_RDONLY);
    if (fd == -1) {
        perror("Open input device");
        return EXIT_FAILURE;
    }
	FD_SET(fd, &fds);
	
    struct input_event ev;
	
	time(&start);
    while (1){
		FD_ZERO(&fds);
		FD_SET(fd, &fds);
		int ret = select(fd + 1, &fds, NULL, NULL, &timeout);
		if (ret > 0 && FD_ISSET(fd, &fds)){
				ssize_t n = read(fd, &ev, sizeof(ev));
				if (n == sizeof(ev)) {
					//if (g_FactoryPressed) {
					if (ev.type == EV_KEY && ev.code == KEY_FACTORYRESET && ev.value == 1){
						printf("Factory Button Released ...\n");
						g_Success=RESULT_SUCCESS;
						g_FactoryPressed=0;
						continue;
					} else 
					//}
					if (ev.type == EV_KEY && ev.code == KEY_FACTORYRESET && ev.value == 0) {
						printf("Factory Button Pressed ...\n");

						if (g_FactoryPressed==0)
							time(&press_time);
						g_FactoryPressed=1;
						continue;
					}
				}
		}
		//printf(".\n");
		if (g_FactoryPressed && current_time() - press_time >= TRIGGER_WAIT_TIME) {
			//g_Success= RESULT_TIMEOUT;
			//break;
			g_FactoryPressed=0;
			printf ("Pressd time greater than %d secs trigger custom evnet\n",TRIGGER_WAIT_TIME);
		}
		sleep(1);
		// if (current_time() - start >= MAX_WAIT_TIME) {
			// g_Success= RESULT_TIMEOUT;
			// break;
		// }
	

    }
	
	switch (g_Success)
	{
		case RESULT_FAILED:
			printf ("Failure\n");
			break;
		case RESULT_SUCCESS:
			printf ("Successful\n");
			break;
		case RESULT_TIMEOUT:
			printf ("Timeout %d Seconds\n",MAX_WAIT_TIME);
			break;
		default:
			printf ("Unknown Result!!");
			break;
			
	}
    close(fd);
    return g_Success;
}
