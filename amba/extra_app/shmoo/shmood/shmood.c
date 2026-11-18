#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <dirent.h>

#include <dirent.h>

#include "utils.h"
#include "logger.h"
#include "json.h"	
#define POLL_SEC  	2
#define DEFAULT_CONFIG_FILE  "/etc/shmoo.json"
#define TEMP_SENSOR_NAME 	 "tmp103"
#define SYSLOG_PORT 514

extern  char hw_ver[32];

typedef struct
{
	char host[128];
    int high;
    int low;
    int duration_min;
	int max_duration_min;
    int sample;

} temp_config_t;

static temp_config_t g_cfg;

static int load_config(const char *file)
{
    FILE *fp;
    long size;
    char *buffer;

    struct json_object *root;
    struct json_object *obj;
    struct json_object *st;

    fp = fopen(file, "r");
    if (!fp)
    {
        perror("fopen");
        return -1;
    }

    fseek(fp, 0, SEEK_END);
    size = ftell(fp);
    rewind(fp);

    buffer = malloc(size + 1);
    if (!buffer)
    {
        fclose(fp);
        return -1;
    }

    fread(buffer, 1, size, fp);
    buffer[size] = 0;

    fclose(fp);

    root = json_tokener_parse(buffer);
    free(buffer);

    if (!root)
    {
        printf("json parse failed\n");
        return -1;
    }

   

    st = json_object_object_get(root, "static");

    obj = json_object_object_get(st, "host");
    char *host_str = json_object_get_string(obj);
	strncpy(g_cfg.host,host_str, json_object_get_string_len(obj));

    obj = json_object_object_get(st, "high");
    g_cfg.high = json_object_get_int(obj);

    obj = json_object_object_get(st, "low");
    g_cfg.low = json_object_get_int(obj);

    obj = json_object_object_get(st, "duration_min");
    g_cfg.duration_min = json_object_get_int(obj);

    obj = json_object_object_get(st, "max_duration_min");
    g_cfg.max_duration_min = json_object_get_int(obj);

    obj = json_object_object_get(st, "sample");
    g_cfg.sample = json_object_get_int(obj);

    json_object_put(root);

    return 0;
}

static int find_hwmon(const char *target,
                      char *output,
                      size_t size)
{
    DIR *dir;
    struct dirent *entry;

    dir = opendir("/sys/class/hwmon");
    if (!dir)
    {
        perror("opendir");
        return -1;
    }

    while ((entry = readdir(dir)) != NULL)
    {
        char path[256];
        char name[128];

        FILE *fp;

        if (entry->d_name[0] == '.')
            continue;

        snprintf(path,
                 sizeof(path),
                 "/sys/class/hwmon/%s/name",
                 entry->d_name);

        fp = fopen(path, "r");
        if (!fp)
            continue;

        fgets(name, sizeof(name), fp);
        fclose(fp);

        /* remove newline */
        name[strcspn(name, "\n")] = 0;

        printf("found hwmon: %s\n", name);

        if (strcmp(name, target) == 0)
        {
            snprintf(output,
                     size,
                     "/sys/class/hwmon/%s/temp1_input",
                     entry->d_name);

            closedir(dir);

            return 0;
        }
    }

    closedir(dir);

    return -1;
}

static int read_temp()
{
    FILE *fp;
    int temp_milli;
	static char hwmon_path[1024]={0};
	if (strlen (hwmon_path) == 0 ) {
		find_hwmon("tmp103",
               hwmon_path,
               sizeof(hwmon_path));
	}
    fp = fopen(hwmon_path, "r");
    if (!fp)
    {
        perror("open temp");
        return -999;
    }

    fscanf(fp, "%d", &temp_milli);
    fclose(fp);

    return temp_milli / 1000;
}

static void trigger_action(int temp)
{
    printf("TRIGGER ACTION temp=%d\n", temp);
	if (temp >= g_cfg.high ) {
		system("/usr/local/bin/cec_auto_shmoo.sh high");
		send_syslog(g_cfg.host,SYSLOG_PORT,"TRIGGER High");		
	}
	else if ( temp <= g_cfg.low){
		system("/usr/local/bin/cec_auto_shmoo.sh low");
		send_syslog(g_cfg.host,SYSLOG_PORT,"TRIGGER Low");
    } 
	else {
		system("/usr/local/bin/cec_auto_shmoo.sh normal");
		send_syslog(g_cfg.host,SYSLOG_PORT,"TRIGGER Normal");
    } 
	/*popen ddrc_v2 instead*/
}

int main(int argc, char *argv[])
{
    time_t exceed_start = 0;
	int i;
   // int trigger_count = 0;
	char config_path[256]={0};
	char ver[1024]={0};
	char msg[2048]={0};
    if (argc != 2)
    {
			snprintf(config_path,sizeof(config_path),"%s",DEFAULT_CONFIG_FILE);
    } else {
		snprintf(config_path,sizeof(config_path),"%s",argv[1]);
	}

    if (load_config(config_path) < 0)
    {
        printf("load config failed\n");
        return -1;
    }

    printf("host : %s\n", g_cfg.host);
    printf("high threshold : %d\n", g_cfg.high);
    printf("low threshold  : %d\n", g_cfg.low);
    printf("duration(min)  : %d\n", g_cfg.duration_min);
    printf("max_duration(min)  : %d\n", g_cfg.max_duration_min);
    printf("sample         : %d\n", g_cfg.sample);
    
	get_fwver(ver,sizeof(ver));
	
	read_hw_ver();
	snprintf(msg,sizeof(msg),"shmood start: Board:%s,fw:%s",hw_ver,ver);
//	send_syslog(g_cfg.host,SYSLOG_PORT,ver);
	send_syslog(g_cfg.host,SYSLOG_PORT,msg);
    time_t start_time = time(NULL);
	while (1)
    {
        int temp;
        int abnormal = 0;
		
        time_t now = time(NULL);
        temp = read_temp();

        // printf("temp=%d\n", temp);
		
		//send_syslog("alive!");
        if (temp >= g_cfg.high || temp <= g_cfg.low)
        {
            abnormal = 1;
        } else {
			abnormal = 0;
			exceed_start = 0;
		}
		if ( now - start_time >=
				(g_cfg.max_duration_min * 60)
			) 
		{
			send_syslog(g_cfg.host, SYSLOG_PORT,"Timeout");	
			trigger_action(temp);	
			break;
		}

        if (abnormal)
        {
            if (exceed_start == 0)
            {
                exceed_start = time(NULL);

                printf("abnormal started time:%u\n",exceed_start);
            }
            else
            {
                if ((now - exceed_start) >=
                    (g_cfg.duration_min * 60))
                {
					trigger_action(temp);
					break;
                }
            }
        } else {
			exceed_start = 0;
		}
        

        sleep(POLL_SEC);
    }
	send_syslog(g_cfg.host,SYSLOG_PORT,"END");
	printf ("The Task Done !!\n");
    return 0;
}
