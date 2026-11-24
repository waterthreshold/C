/* crc32.c -- compute the CRC-32 of a data stream
 * Copyright (C) 1995-1998 Mark Adler
 * For conditions of distribution and use, see copyright notice in zlib.h
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
#include <getopt.h>

#define PROGRAM_VERSION  "v1.0"
#define MAGIAC_STRING_HEADER  "2385"
#define PROJECTCODE_FILE_NAME	"/etc/fw_version"
#define VERSION_FILE_NAME "/etc/rev_version"
#define DEFAULT_FW_NAME   "web_%s.bin"

int is_indicate_image  = 0;
int is_indicate_code  = 0;
int is_indicate_rootfs  = 0;

typedef struct
{
	unsigned char magic[4];
	unsigned int project_code;
	unsigned int revision;
	unsigned int timestamp;
	unsigned int image_len;
	unsigned int image_crc32;
	unsigned int dtb_len;
	unsigned int dtb_crc32;
	unsigned int rootfs_len;
	unsigned int rootfs_crc32;
	unsigned char reserved[40];
}FW_HEADER_FOAM;

// static struct option long_options[] = {
	// {"help", no_argument , 0 , 'h'},
	// {"vesion", no_argument , 0 , 'v'},
	// {"code", required_argument, 0, 'C'},
	// {"image", required_argument, 0, 'I'}, 
	// {"root", required_argument, 0, 'R'},
	// {0,0,0,0}
// };

struct description_s {
	const char opt;
	const char *des;
};

 // const struct description_s descs[] = {
	// {'h', "show simpliciy help description"},
	// {'v', "print program version"},
	// {'C', "project code. Example: Larnaca2 is 2416"},
	// {'I', "indicate the Kernel image path"},
	// {'R', "Indicate the rootfs image path"},
	// {'o', "output file firmware"},
	// {-1,NULL}
// };
#ifdef CRC32_FAST
static const unsigned int crc_table[256] = {
	0x00000000L, 0x77073096L, 0xee0e612cL, 0x990951baL, 0x076dc419L,
	0x706af48fL, 0xe963a535L, 0x9e6495a3L, 0x0edb8832L, 0x79dcb8a4L,
	0xe0d5e91eL, 0x97d2d988L, 0x09b64c2bL, 0x7eb17cbdL, 0xe7b82d07L,
	0x90bf1d91L, 0x1db71064L, 0x6ab020f2L, 0xf3b97148L, 0x84be41deL,
	0x1adad47dL, 0x6ddde4ebL, 0xf4d4b551L, 0x83d385c7L, 0x136c9856L,
	0x646ba8c0L, 0xfd62f97aL, 0x8a65c9ecL, 0x14015c4fL, 0x63066cd9L,
	0xfa0f3d63L, 0x8d080df5L, 0x3b6e20c8L, 0x4c69105eL, 0xd56041e4L,
	0xa2677172L, 0x3c03e4d1L, 0x4b04d447L, 0xd20d85fdL, 0xa50ab56bL,
	0x35b5a8faL, 0x42b2986cL, 0xdbbbc9d6L, 0xacbcf940L, 0x32d86ce3L,
	0x45df5c75L, 0xdcd60dcfL, 0xabd13d59L, 0x26d930acL, 0x51de003aL,
	0xc8d75180L, 0xbfd06116L, 0x21b4f4b5L, 0x56b3c423L, 0xcfba9599L,
	0xb8bda50fL, 0x2802b89eL, 0x5f058808L, 0xc60cd9b2L, 0xb10be924L,
	0x2f6f7c87L, 0x58684c11L, 0xc1611dabL, 0xb6662d3dL, 0x76dc4190L,
	0x01db7106L, 0x98d220bcL, 0xefd5102aL, 0x71b18589L, 0x06b6b51fL,
	0x9fbfe4a5L, 0xe8b8d433L, 0x7807c9a2L, 0x0f00f934L, 0x9609a88eL,
	0xe10e9818L, 0x7f6a0dbbL, 0x086d3d2dL, 0x91646c97L, 0xe6635c01L,
	0x6b6b51f4L, 0x1c6c6162L, 0x856530d8L, 0xf262004eL, 0x6c0695edL,
	0x1b01a57bL, 0x8208f4c1L, 0xf50fc457L, 0x65b0d9c6L, 0x12b7e950L,
	0x8bbeb8eaL, 0xfcb9887cL, 0x62dd1ddfL, 0x15da2d49L, 0x8cd37cf3L,
	0xfbd44c65L, 0x4db26158L, 0x3ab551ceL, 0xa3bc0074L, 0xd4bb30e2L,
	0x4adfa541L, 0x3dd895d7L, 0xa4d1c46dL, 0xd3d6f4fbL, 0x4369e96aL,
	0x346ed9fcL, 0xad678846L, 0xda60b8d0L, 0x44042d73L, 0x33031de5L,
	0xaa0a4c5fL, 0xdd0d7cc9L, 0x5005713cL, 0x270241aaL, 0xbe0b1010L,
	0xc90c2086L, 0x5768b525L, 0x206f85b3L, 0xb966d409L, 0xce61e49fL,
	0x5edef90eL, 0x29d9c998L, 0xb0d09822L, 0xc7d7a8b4L, 0x59b33d17L,
	0x2eb40d81L, 0xb7bd5c3bL, 0xc0ba6cadL, 0xedb88320L, 0x9abfb3b6L,
	0x03b6e20cL, 0x74b1d29aL, 0xead54739L, 0x9dd277afL, 0x04db2615L,
	0x73dc1683L, 0xe3630b12L, 0x94643b84L, 0x0d6d6a3eL, 0x7a6a5aa8L,
	0xe40ecf0bL, 0x9309ff9dL, 0x0a00ae27L, 0x7d079eb1L, 0xf00f9344L,
	0x8708a3d2L, 0x1e01f268L, 0x6906c2feL, 0xf762575dL, 0x806567cbL,
	0x196c3671L, 0x6e6b06e7L, 0xfed41b76L, 0x89d32be0L, 0x10da7a5aL,
	0x67dd4accL, 0xf9b9df6fL, 0x8ebeeff9L, 0x17b7be43L, 0x60b08ed5L,
	0xd6d6a3e8L, 0xa1d1937eL, 0x38d8c2c4L, 0x4fdff252L, 0xd1bb67f1L,
	0xa6bc5767L, 0x3fb506ddL, 0x48b2364bL, 0xd80d2bdaL, 0xaf0a1b4cL,
	0x36034af6L, 0x41047a60L, 0xdf60efc3L, 0xa867df55L, 0x316e8eefL,
	0x4669be79L, 0xcb61b38cL, 0xbc66831aL, 0x256fd2a0L, 0x5268e236L,
	0xcc0c7795L, 0xbb0b4703L, 0x220216b9L, 0x5505262fL, 0xc5ba3bbeL,
	0xb2bd0b28L, 0x2bb45a92L, 0x5cb36a04L, 0xc2d7ffa7L, 0xb5d0cf31L,
	0x2cd99e8bL, 0x5bdeae1dL, 0x9b64c2b0L, 0xec63f226L, 0x756aa39cL,
	0x026d930aL, 0x9c0906a9L, 0xeb0e363fL, 0x72076785L, 0x05005713L,
	0x95bf4a82L, 0xe2b87a14L, 0x7bb12baeL, 0x0cb61b38L, 0x92d28e9bL,
	0xe5d5be0dL, 0x7cdcefb7L, 0x0bdbdf21L, 0x86d3d2d4L, 0xf1d4e242L,
	0x68ddb3f8L, 0x1fda836eL, 0x81be16cdL, 0xf6b9265bL, 0x6fb077e1L,
	0x18b74777L, 0x88085ae6L, 0xff0f6a70L, 0x66063bcaL, 0x11010b5cL,
	0x8f659effL, 0xf862ae69L, 0x616bffd3L, 0x166ccf45L, 0xa00ae278L,
	0xd70dd2eeL, 0x4e048354L, 0x3903b3c2L, 0xa7672661L, 0xd06016f7L,
	0x4969474dL, 0x3e6e77dbL, 0xaed16a4aL, 0xd9d65adcL, 0x40df0b66L,
	0x37d83bf0L, 0xa9bcae53L, 0xdebb9ec5L, 0x47b2cf7fL, 0x30b5ffe9L,
	0xbdbdf21cL, 0xcabac28aL, 0x53b39330L, 0x24b4a3a6L, 0xbad03605L,
	0xcdd70693L, 0x54de5729L, 0x23d967bfL, 0xb3667a2eL, 0xc4614ab8L,
	0x5d681b02L, 0x2a6f2b94L, 0xb40bbe37L, 0xc30c8ea1L, 0x5a05df1bL,
	0x2d02ef8dL
};

#define DO1(buf) crc = crc_table[((int)crc ^ (*buf++)) & 0xff] ^ (crc >> 8);
#define DO2(buf)  DO1(buf); DO1(buf);
#define DO4(buf)  DO2(buf); DO2(buf);
#define DO8(buf)  DO4(buf); DO4(buf);

unsigned int crc32(const unsigned char *buffer, unsigned int len)
{
	unsigned int crc;
	crc = 0;
	crc = crc ^ 0xffffffffL;
	while(len >= 8) {
		DO8(buffer);
		len -= 8;
	}
	if(len) do {
		DO1(buffer);
	} while(--len);
	return crc ^ 0xffffffffL;
}
#else
unsigned int crc32(const unsigned char *message, unsigned int len) {
   int i, j;
   unsigned int byte, crc, mask;

   i = 0;
   crc = 0xFFFFFFFF;
   while (i < len) {
      byte = message[i];            // Get next byte.
      crc = crc ^ byte;
      for (j = 7; j >= 0; j--) {    // Do eight times.
         mask = -(crc & 1);
         crc = (crc >> 1) ^ (0xEDB88320 & mask);
      }
      i = i + 1;
   }
   return ~crc;
}
#endif
// char *get_soc_name(){
	// char s[128]= {0};
	// int fd;
	// fd = open(".soc", O_RDONLY);
	// if (fd == ENOENT )
	// {
		// perror("No such file or directory");
		// exit(1);
	// } else if (fd > 0) {
		// read (fd,s,128);
	// } else {
		// perror("%s: Unknown read Issue",__file__);
		// exit(1);
	// }
	
	// return s;
// }

// char *get_board_type(){
	// char s[128]= {0};
	// int fd;
	// fd = open(".soc", O_RDONLY);
	// if (fd == ENOENT )
	// {
		// perror("%s: No such file or directory");
		// exit(1);
	// } else if (fd > 0) {
		// read (fd,s,128);
	// } else {
		// perror("%s: Unknown read Issue",__file__);
		// exit(1);
	// }
	
	// return s;
// }
// static void usage (char *prg){
	// int i,j;
	// printf("Usage: %s [OPTION]  [ARGUMENTS]\n", prg);
	// for (i = 0; i < sizeof(long_options) / sizeof(long_options[0]) - 1; i++) {
		// if (isalpha(long_options[i].val))
			// printf("-%c ", long_options[i].val);
		// else
			// printf("   ");
		// printf("--%s", long_options[i].name);
		// for (j = 0 ; descs[j].opt > 0  ;j++) {
			// if (long_options[i].val == descs[j].opt){
				// printf("\t%s\n", descs[j].des);
				// break;
			// }
		// }
	// }
	// printf("\n");
	// printf("Examples:\n"
			// "  upgrade_partition -e /dev/mtd3 --show_env\n"
			// "	    Show the env partition of MTD device /dev/mtd3\n"
			// "  upgrade_partition -p /dev/mtd7 /tmp/kernelb.img\n"
			// "	    Upgrde the kernelb.img to MTD device /dev/mtd7\n"
			// "  upgrade_partition -e /dev/mtd3 -k -P kernelb\n"
			// "	    Upgrde the env partition of MTD device /dev/mtd3\n"
			// "	    to switch kernelb image for kernel boot meta\n"
			// "  upgrade_partition -e /dev/mtd3 -E -i 0 --mask 255.255.255.0\n" 
			// "                    --gw 10.0.0.1 --ip 10.0.0.2 --mac 12:34:56:78:01:02\n"
			// "	    Set the eth0 net configuration\n"
			// "  upgrade_partition -e /dev/mtd3 -K --tftpd_file kernel.bin --tftpd_addr 0x00200000\n"
			// "	    Specify the tftpd fetched kernel file name\n");
	// exit(0);
// }

static void version(){
	printf("Version" PROGRAM_VERSION "\n"
			"\n"
			"Copyright (C) 2026 Jeff Chiang @ Chicony \n"
			"\n");
	exit(0);
}

static void parser_options(int argc, char *argv[]){
	int error = 0;
	int ch;
	int option_index = 0;
	static const char *short_options = "hvC:I:R:";
	// while ((ch = getopt_long(argc, argv, short_options, long_options, &option_index)) != -1) {
		// switch (ch) {
			// case 'h':
				// usage (argv[0]);
				// break;
			// case 'v'
				// version();
				// break;
			// case 'C':
				// break;
			// case 'I'
				// break;
			// case 'R':
				// break;
		// }
	// }
}
 
int main (int argc, char *argv[]) {
	struct stat s,rootfs_s,dtb_s;
	
	FW_HEADER_FOAM *h = malloc(sizeof(FW_HEADER_FOAM));
	memset(h,0,sizeof(FW_HEADER_FOAM) );
	//int n = s.st_size;
//	parser_options (argc, argv);
	//printf("Probook91222Probook912221\n");
	memcpy(h->magic, MAGIAC_STRING_HEADER, sizeof(h->magic));
	h->project_code=2416;
	//if (is_root_path_set <= 0 )
	//	snprintf (default_project_code_path
	h->revision=1;
	
	time_t timestamp = time(NULL);
	h->timestamp=(unsigned int) timestamp;
	printf ("timestamp: %u\n", h->timestamp);
	stat("Image", &s);
	h->image_len =s.st_size;
	int image_fd = open ("Image",O_RDONLY);
	if ( image_fd < 0 )
	{
		perror ("No such file");
		exit(1);
	}
	char *k_buffer= (char *) malloc (s.st_size);
	memset(k_buffer,0,s.st_size);
	read(image_fd,k_buffer,s.st_size);
	h->image_crc32 = crc32(k_buffer,s.st_size);
	//printf ("%x\n",h->image_crc32);
	stat("rootfs.ext4", &rootfs_s);
	h->rootfs_len= rootfs_s.st_size;
	//printf ("rootfs length: %u", h->rootfs_len);
	int rootfs_fd = open ("rootfs.ext4", O_RDONLY);
	if ( rootfs_fd < 0 )
	{
		perror ("No such file");
		exit(1);
	}
	char *r_buffer= (char *) malloc (rootfs_s.st_size);
	memset(r_buffer,0,rootfs_s.st_size);
	read(rootfs_fd,r_buffer,rootfs_s.st_size);
	h->rootfs_crc32 = crc32(r_buffer,rootfs_s.st_size); 
	printf ("[kernel] crc32=%x, lens=%d\n",h->image_crc32,h->image_len);
	printf ("[rootfs] crc32=%x, Lens=%d\n",h->rootfs_crc32,h->rootfs_len);
	// Initilaize firmware header
	stat("cv5_larnaca2.dtb", &dtb_s);
	int dtb_fd = open ("cv5_larnaca2.dtb",O_RDONLY);
	
	if ( dtb_fd < 0 ){
		perror ("No such dtb file");
		exit (1);
	}
	char *dtb_buffer =(char *) malloc(dtb_s.st_size);
	memset(dtb_buffer, 0 , dtb_s.st_size);
	read(dtb_fd,dtb_buffer,dtb_s.st_size);
	h->dtb_len  = dtb_s.st_size;
	h->dtb_crc32 = crc32(dtb_buffer,h->dtb_len);
	printf ("[DTB] crc32=%X, size=%d\n",h->dtb_crc32,h->dtb_len);	
	int fw_fd;	
	if ((fw_fd = open("fw.bin", O_CREAT | O_WRONLY, 0644)) < 0)
	{
		perror ("No such file");
		exit(1);
	}
	write(fw_fd,(FW_HEADER_FOAM *)h, sizeof(FW_HEADER_FOAM));
	write(fw_fd,k_buffer,h->image_len);	
	write(fw_fd,dtb_buffer,h->dtb_len);	
	write(fw_fd,r_buffer,h->rootfs_len);	
	// int read_n = read(fd, k_buffer, n);
	// printf ("%x\n",crc32(k_buffer, read_n));
	
	if (k_buffer){			
		free(k_buffer);
	}
	if (r_buffer){	
		free(r_buffer);
	}
	if (dtb_buffer){	
		free(dtb_buffer);
	}
	close (fw_fd);
	close(rootfs_fd);
	close(image_fd);
	close(dtb_fd);
	return 0;
}
