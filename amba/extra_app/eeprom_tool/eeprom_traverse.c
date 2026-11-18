#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include "eeprom_info.h"
/**
./dump_eeprom -w -i Bosch_eeprom_dump_19B96C_NONEIR.bin  # Read Bosch_eeprom_dump_19B96C_NONEIR.bin write to eeprom

dump_eeprom -o test-write.bin  # dump eeprom data to test-write.bin
 ./eeprom_tool -I -i dump.bin  -o eeprom_test1.json
  ./eeprom_tool -I -i dump.bin  -o eeprom_test1.json 
**/
// Helper function to replace spaces with hyphens in-place


void print_usage(const char *prog_name) {
    fprintf(stderr, "Usage: %s [-w] [-b bus_id] [-i input_file] [-o output_file]\n", prog_name);
    fprintf(stderr, "  -w  Write mode (write backup file to eeprom)\n");
    fprintf(stderr, "  -b <bus_id>     I2C bus ID (default: 2)\n");
    fprintf(stderr, "  -i <input_file> Path to input file\n");
	fprintf(stderr, "  -g <write protect> write protect gpio pin\n");
    fprintf(stderr, "  -o <output_file> Path to output file\n");
	fprintf(stderr, "  -I Show info mode\n");
}

int dump_eeprom( char *input_file, char* output_file) {
		
	
		int fd = open(input_file, O_RDONLY);
		if (fd < 0) {
			perror("Failed to open source device/file");
			return 1;
		}

		unsigned char length_buf[2];
		unsigned char index_buf[2];

		char name_index_7[256] = "";
		char tail_index_31[256] = "";

		int found_17 = 0;
		int found_31 = 0;

		// Traverse the EEPROM/file sequence
		while (1) {
			ssize_t bytes_read = read(fd, length_buf, 2);
			if (bytes_read < 2) {
				break; 
			}
			uint16_t data_len = (length_buf[0] << 8) | length_buf[1];

			bytes_read = read(fd, index_buf, 2);
			if (bytes_read < 2) {
				break;
			}
			uint16_t data_index = (index_buf[0] << 8) | index_buf[1];

			if (data_len == 0 || data_len > 1024) {
				break;
			}

			unsigned char *payload = malloc(data_len);
			if (!payload) {
				perror("Memory allocation failed");
				close(fd);
				return 1;
			}

			bytes_read = read(fd, payload, data_len);
			if (bytes_read < data_len) {
				free(payload);
				break;
			}

			if (data_index == 7) {
				int copy_len = data_len < sizeof(name_index_7) - 1 ? data_len : sizeof(name_index_7) - 1;
				memcpy(name_index_7, payload, copy_len);
				name_index_7[copy_len] = '\0';
				found_17 = 1;
			} else if (data_index == 31) {
				int copy_len = data_len < sizeof(tail_index_31) - 1 ? data_len : sizeof(tail_index_31) - 1;
				memcpy(tail_index_31, payload, copy_len);
				tail_index_31[copy_len] = '\0';
				found_31 = 1;
			}

			free(payload);
		}

		if (!found_17 || !found_31) {
			fprintf(stderr, "Error: Could not find both index 17 and index 31.\n");
			close(fd);
			return 1;
		}

		// Format index 17: replace spaces with '-'
		replace_charater(name_index_7, ' ', '-');

		// Determine final output filename (use -o override if provided, otherwise auto-generate)
		char final_filename[512];
		if (output_file) {
			snprintf(final_filename, sizeof(final_filename), "%s", output_file);
		} else {
			snprintf(final_filename, sizeof(final_filename), "%s-%s.bin", name_index_7, tail_index_31);
		}

		int out_fd = open(final_filename, O_WRONLY | O_CREAT | O_EXCL, 0644);
		if (out_fd < 0) {
			perror("Failed to create destination file descriptor");
			close(fd);
			return 1;
		}

		// Reset source file offset back to the beginning for full copy
		if (lseek(fd, 0, SEEK_SET) < 0) {
			perror("Failed to seek source file");
			close(fd);
			close(out_fd);
			return 1;
		}

		// Stream source content into final_filename
		char copy_buf[4096] = {0};
		ssize_t r_bytes;
		ssize_t w_bytes_total = 0;
		while ((r_bytes = read(fd, copy_buf, sizeof(copy_buf))) > 0) {
			ssize_t w_bytes = write(out_fd, copy_buf, r_bytes);
			if (w_bytes != r_bytes) {
				perror("Failed to write to destination file");
				close(fd);
				close(out_fd);
				return 1;
			}
			w_bytes_total += w_bytes;
		}

		close(fd);
		close(out_fd);

		//printf("Mode: dump | Bus ID: %s\n", bus_id);
		printf("Dump successfully created file and wrote data to: %s (%ld bytes)\n", final_filename, (long)w_bytes_total);
		return 0;
}

int write_eeprom( char *input_file, char* output_file, int gpio) {
	
	char cmd[1024] = {0};
	if (input_file == NULL){
		perror("Write: input file");
		return 1;
	}
	int fd = open(input_file, O_RDONLY);
	if (fd < 0) {
		perror("Failed to open source device/file");
		return 1;
	}
	int out_fd = open(output_file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (out_fd < 0) {
		perror("Failed to create destination file descriptor");
		close(fd);
		return 1;
	}
	
  	snprintf(cmd, sizeof(cmd), "amba_debug -g %d -d 0", gpio);
    int ret = system(cmd);
    if (ret != 0) {
        fprintf(stderr, "Warning: amba_debug command returned non-zero exit status\n");
    }
    
    sleep(1); // Wait for hardware state to settle
    
    // Stream data from input file descriptor to output file descriptor
    char copy_buf[4096];
    ssize_t r_bytes;
    ssize_t w_bytes_total = 0;
    
    while ((r_bytes = read(fd, copy_buf, sizeof(copy_buf))) > 0) {
        ssize_t w_bytes_written = 0;
        while (w_bytes_written < r_bytes) {
            ssize_t w_bytes = write(out_fd, copy_buf + w_bytes_written, r_bytes - w_bytes_written);
            if (w_bytes < 0) {
                perror("Failed to write to destination file");
                close(fd);
                close(out_fd);
                return 1;
            }
            w_bytes_written += w_bytes;
        }
        w_bytes_total += w_bytes_written;
    }
    
    // Clean up file descriptors
    close(fd);
    close(out_fd);
    
    printf("Write successfully copied %ld bytes to: %s\n", (long)w_bytes_total, output_file);
	snprintf(cmd, sizeof(cmd), "amba_debug -g %d -d 1", gpio);
    ret = system(cmd);
    if (ret != 0) {
        fprintf(stderr, "Warning: amba_debug command returned non-zero exit status\n");
    }
    return 0;
	
	//read from fd to out_fd
}
int main(int argc, char *argv[]) {
    int write_mode = 0, info_mode= 0;
    char bus_id[32] = "2";          // Default bus ID
	char wp_pin=63;				//default gpio pin
    char *input_file = NULL;
    char *output_file = NULL;

    int opt;
    // 'w' is a flag (no colon), while b, i, o take arguments (followed by colons)
    while ((opt = getopt(argc, argv, "wIb:i:o:")) != -1) {
        switch (opt) {
            case 'w':
                write_mode = 1;
                break;
            case 'b':
                strncpy(bus_id, optarg, sizeof(bus_id) - 1);
                bus_id[sizeof(bus_id) - 1] = '\0';
                break;
            case 'i':
                input_file = optarg;
                break;
            case 'o':
                output_file = optarg;
                break;
			case 'g':
				if (atoi(optarg) > 0 )
						wp_pin = atoi(optarg);
                break;
			case 'I':
				info_mode=1;
				break;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    char eeprom_path[256];
	snprintf(eeprom_path, sizeof(eeprom_path), "/sys/bus/i2c/devices/%s-0054/eeprom", bus_id);
#if 1
	if (info_mode ) {
		char *source_path = input_file ? input_file : eeprom_path;
		show_info(source_path,output_file);
	} else
#endif
	if (write_mode) {
		char *source_path = eeprom_path;
		write_eeprom(input_file,source_path,wp_pin);
	} else {
		char *source_path = input_file ? input_file : eeprom_path;
		dump_eeprom(source_path,output_file);
	}
  
    return 0;
}
