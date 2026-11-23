#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <cjson/cJSON.h>

#define PGM_MAGIC   "KSON PGM"
#define PGM_NUMBER1 6
#define PGM_NUMBER2 1
#define PGM_NUMBER3 0

#define SAFE_HIGH_TEMP_MIN  45
#define SAFE_LOW_TEMP_MIN   -35

typedef struct __attribute__((packed))
{
    char magic[8];
    int num[3];
    int length;
    int chksum;
} PGM_HEADER;

typedef struct __attribute__((packed))
{
    float temp;
    float humidity;
    unsigned short hour;
    unsigned short min;
    unsigned char p1;
    unsigned char p2;
    unsigned char p3;
    unsigned char wt;
} PGM_ROW_TEMP;

typedef struct __attribute__((packed))
{
    short cycle;
    short row_temp_count;

    float safe_high_temp;
    float safe_low_temp;

    short year;
    unsigned char month;
   unsigned char day;
    unsigned char hour;
    unsigned char min;

    PGM_ROW_TEMP *temp;

} PGM_METADATA;

static char *read_file(const char *filename)
{
    FILE *fp;
    long size;
    char *buf;

    fp = fopen(filename, "rb");
    if (!fp)
    {
        perror(filename);
        return NULL;
    }

    fseek(fp, 0, SEEK_END);
    size = ftell(fp);
    rewind(fp);

    buf = malloc(size + 1);
    if (!buf)
    {
        fclose(fp);
        return NULL;
    }

    fread(buf, 1, size, fp);
    buf[size] = '\0';

    fclose(fp);
    return buf;
}

static void fill_current_time(PGM_METADATA *meta)
{
    time_t now;
    struct tm *tm_info;

    time(&now);
    tm_info = localtime(&now);

    meta->year  = tm_info->tm_year + 1900;
    meta->month = tm_info->tm_mon + 1;
    meta->day   = tm_info->tm_mday;
    meta->hour  = tm_info->tm_hour;
    meta->min   = tm_info->tm_min;
}

static int parse_json(const char *filename, PGM_METADATA *meta)
{
    char *json_buf;
    cJSON *root;
    cJSON *metadata;
    cJSON *rows;
    int count;
    int i;

    memset(meta, 0, sizeof(*meta));

    json_buf = read_file(filename);
    if (!json_buf)
        return -1;

    root = cJSON_Parse(json_buf);
    free(json_buf);

    if (!root)
    {
        printf("JSON parse failed\n");
        return -1;
    }

    metadata = cJSON_GetObjectItem(root, "metadata");
    if (!metadata)
    {
        cJSON_Delete(root);
        return -1;
    }

    meta->cycle =
        cJSON_GetObjectItem(metadata, "cycle")->valueint;
/*
    meta->safe_high_temp =
        (float)cJSON_GetObjectItem(metadata,
                                   "safe_high_temp")->valuedouble;

    meta->safe_low_temp =
        (float)cJSON_GetObjectItem(metadata,
                                   "safe_low_temp")->valuedouble;
*/
    rows = cJSON_GetObjectItem(root, "row_temp");
    if (!rows)
    {
        cJSON_Delete(root);
        return -1;
    }

    count = cJSON_GetArraySize(rows);

    meta->row_temp_count = count;

    meta->temp = calloc(count, sizeof(PGM_ROW_TEMP));
    if (!meta->temp)
    {
        cJSON_Delete(root);
        return -1;
    }
	float high_max=-9999;
	float low_min=9999;
    for (i = 0; i < count; i++)
    {
        cJSON *row = cJSON_GetArrayItem(rows, i);

        meta->temp[i].temp =
            (float)cJSON_GetObjectItem(row, "temp")->valuedouble;
		
		if (meta->temp[i].temp > high_max){
			high_max = meta->temp[i].temp;
		}	
		else if (meta->temp[i].temp < low_min){
			low_min = meta->temp[i].temp;
		}
		
        meta->temp[i].humidity =
            (float)cJSON_GetObjectItem(row, "humidity")->valuedouble;

        meta->temp[i].hour =
            cJSON_GetObjectItem(row, "hour")->valueint;

        meta->temp[i].min =
            cJSON_GetObjectItem(row, "min")->valueint;

        meta->temp[i].p1 =
            cJSON_GetObjectItem(row, "p1")->valueint;

        meta->temp[i].p2 =
            cJSON_GetObjectItem(row, "p2")->valueint;

        meta->temp[i].p3 =
            cJSON_GetObjectItem(row, "p3")->valueint;

        meta->temp[i].wt =
            cJSON_GetObjectItem(row, "wt")->valueint;
    }
	if  ( high_max + 5 < SAFE_HIGH_TEMP_MIN ){
		meta->safe_high_temp = SAFE_HIGH_TEMP_MIN;
	} else{
		meta->safe_high_temp = high_max + 5;
	
	} 
	if (low_min - 5 > SAFE_LOW_TEMP_MIN ) {
		meta->safe_low_temp = SAFE_LOW_TEMP_MIN;
	} else {
		meta->safe_low_temp = low_min - 5 ;
	}
    fill_current_time(meta);

    cJSON_Delete(root);

    return 0;
}

static unsigned int calculate_checksum(const PGM_METADATA *meta)
{
    unsigned int sum = 0;
    size_t i;
    int row;

    const unsigned char *ptr =
        (const unsigned char *)meta;

    size_t metadata_size =
        sizeof(PGM_METADATA) - sizeof(PGM_ROW_TEMP *);

    for (i = 0; i < metadata_size; i++)
        sum += ptr[i];

    for (row = 0; row < meta->row_temp_count; row++)
    {
        const unsigned char *p =
            (const unsigned char *)&meta->temp[row];

        for (i = 0; i < sizeof(PGM_ROW_TEMP); i++)
            sum += p[i];
    }

    return sum;
}

static int write_pgm(const char *filename,
                     const PGM_METADATA *meta)
{
    FILE *fp;
    PGM_HEADER header;

    memset(&header, 0, sizeof(header));

    memcpy(header.magic,
           PGM_MAGIC,
           strlen(PGM_MAGIC));

    header.num[0] = PGM_NUMBER1;
    header.num[1] = PGM_NUMBER2;
    header.num[2] = PGM_NUMBER3;

    header.length =
        sizeof(PGM_METADATA) -
        sizeof(PGM_ROW_TEMP *) +
        meta->row_temp_count * sizeof(PGM_ROW_TEMP);

    header.chksum =
        calculate_checksum(meta);

    fp = fopen(filename, "wb");
    if (!fp)
    {
        perror(filename);
        return -1;
    }

    fwrite(&header,
           sizeof(header),
           1,
           fp);

    fwrite(meta,
           sizeof(PGM_METADATA) -
           sizeof(PGM_ROW_TEMP *),
           1,
           fp);

    fwrite(meta->temp,
           sizeof(PGM_ROW_TEMP),
           meta->row_temp_count,
           fp);

    fclose(fp);

    return 0;
}

static void dump_metadata(const PGM_METADATA *meta)
{
    int i;

    printf("cycle=%d\n", meta->cycle);
    printf("row_count=%d\n", meta->row_temp_count);
    printf("safe_high=%.2f\n", meta->safe_high_temp);
    printf("safe_low=%.2f\n", meta->safe_low_temp);

    for (i = 0; i < meta->row_temp_count; i++)
    {
        printf("[%d] temp=%.2f humidity=%.2f "
               "hour=%u min=%u wt=%u\n",
               i,
               meta->temp[i].temp,
               meta->temp[i].humidity,
               meta->temp[i].hour,
               meta->temp[i].min,
               meta->temp[i].wt);
    }
}

int main(int argc, char *argv[])
{
    PGM_METADATA meta;

    if (argc != 3)
    {
        printf("Usage:\n");
        printf("    %s input.json output.pgm\n",
               argv[0]);
        return 1;
    }

    if (parse_json(argv[1], &meta))
    {
        printf("Failed to parse json\n");
        return 1;
    }

    dump_metadata(&meta);

    if (write_pgm(argv[2], &meta))
    {
        printf("Failed to write pgm file\n");
        free(meta.temp);
        return 1;
    }

    printf("PGM file created: %s\n",
           argv[2]);

    free(meta.temp);

    return 0;
}
