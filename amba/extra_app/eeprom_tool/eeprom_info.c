#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include "eeprom_info.h"
#include "cJSON.h" // Requires cJSON library headers


 const TagMeta TAG_TABLE[] = {
    {"TagVersion", 1, 1, TYPE_NUM},
    {"ProductId", 2, 1, TYPE_NUM},
    {"VarintId", 3, 1, TYPE_NUM},
    {"EthernetMacAddress", 4, 1, TYPE_HEX},
    {"Signature", 5, 0, TYPE_HEX},
    {"SerialNumber", 6, 1, TYPE_STRING},
    {"MaterialDescription", 7, 1, TYPE_STRING},
    {"Ctn", 8, 1, TYPE_STRING},
    {"SapCode", 9, 1, TYPE_STRING},
    {"Rev", 10, 0, TYPE_STRING},
    {"TypeCode", 11, 0, TYPE_NUM},
    {"MinfFwVersion", 15, 0, TYPE_HEX},
    {"Platform", 16, 0, TYPE_STRING},
    {"PriductFamilyName", 17, 1, TYPE_STRING},
    {"Project", 18, 0, TYPE_STRING},
    {"MinumumFirmwarevVersion", 19, 1, TYPE_HEX},
    {"ManufacturingDate", 20, 1, TYPE_HEX},
    {"NumberOfmacs", 21, 0, TYPE_NUM},
    {"LabelMac", 31, 0, TYPE_STRING},
    {"UnkonownCode1", 32, 0, TYPE_HEX},
    {"EepromWriteProtectGpio", 24, 0, TYPE_NUM},
    {"OriginalVarintId", 53, 0, TYPE_NUM},
    {"ReleaseStatus", 54, 0, TYPE_STRING},
    {"UnkonownCode", 55, 0, TYPE_HEX},
    {"ManufacturingSignDate", 56, 0, TYPE_HEX}
};

void replace_charater(char *str, char src, char target) {
    if (!str) return;

    int read_idx = 0;
    int write_idx = 0;

    while (str[read_idx] != '\0') {
        if (str[read_idx] == src) {
            // If target is '\0', delete the character by skipping it
            if (target == '\0') {
                // Do nothing (skip writing)
            } else {
                // Otherwise, replace it with the target character
                str[write_idx++] = target;
            }
        } else {
            // Keep normal characters
            str[write_idx++] = str[read_idx];
        }
        read_idx++;
    }
    
    // Properly terminate the new shorter string
    str[write_idx] = '\0';
}
int show_info( char *input_file,  char *output_file) {
	
	if (output_file && strlen(output_file) > 0) {
        if (strcmp(input_file, output_file) == 0) {
            fprintf(stderr, "Error: input_file (%s) and output_file (%s) cannot be the same file.\n", 
                    input_file, output_file);
            exit(EFILENOTEXIST);
        }
    }
	
    int fd = open(input_file, O_RDONLY);
    if (fd < 0) {
        perror("Failed to open input file/device");
        exit(EFILENOTEXIST);
    }

    cJSON *root = NULL;
    cJSON *data_obj = NULL,*label_obj=NULL;
    int is_json_mode = (output_file != NULL && strlen(output_file) > 0);

    // If output file is provided, initialize the cJSON structure: {"data": {}}
    if (is_json_mode) {
        root = cJSON_CreateObject();
        data_obj = cJSON_CreateObject();
		label_obj = cJSON_CreateObject();
        cJSON_AddItemToObject(root, "data", data_obj);
		cJSON_AddItemToObject(root, "label", label_obj);
    } else {
        printf("--- Parsing EEPROM Info from: %s ---\n", input_file);
    }

    unsigned char length_buf[2];
    unsigned char index_buf[2];
	char ctn[128]={0};
	char mac[128]={0};
	char sn[128]={0};
	char sap[128]= {0};
	char BoxLabel2DCode[2048]={0};
	char ProductLabel2DCode[2048]={0};
	char InstallerLabelQRCode[2048]={0};
    // Traverse the EEPROM/file sequence
    while (1) {
        ssize_t bytes_read = read(fd, length_buf, 2);
        if (bytes_read < 2) break;
        uint16_t data_len = (length_buf[0] << 8) | length_buf[1];

        bytes_read = read(fd, index_buf, 2);
        if (bytes_read < 2) break;
        uint16_t data_index = (index_buf[0] << 8) | index_buf[1];

        if (data_len == 0 || data_len > 1024) break;

        unsigned char *payload = malloc(data_len + 1);
        if (!payload) {
            perror("Memory allocation failed");
            break;
        }

        bytes_read = read(fd, payload, data_len);
        if (bytes_read < data_len) {
            free(payload);
            break;
        }
        payload[data_len] = '\0'; // Safe null-termination

        // Search for mapping in TAG_TABLE
        const TagMeta *meta = NULL;
        for (size_t i = 0; i < TAG_TABLE_SIZE; i++) {
            if (TAG_TABLE[i].index == data_index) {
                meta = &TAG_TABLE[i];
                break;
            }
        }
		if (data_index == 6  ) // sn
		{
			memcpy(sn, payload,data_len);
		}
		else if (data_index == 4  )  //mac
		{
			 // for (size_t i = 0; i < data_len <6; i++) {
				snprintf(mac,sizeof(mac) ,"%02X:%02X:%02X:%02X:%02X:%02X", payload[0], payload[1], payload[2], payload[3], payload[4], payload[5]);
				// offset += 2;
			// }
		}
		else if (data_index == 8 ) { //ctn
			memcpy(ctn, payload,data_len);
		}
		else if (data_index == 9 ) { //sap
			
			memcpy(sap, payload,data_len);
			replace_charater(sap,'.','\0');
		}
		
        if (meta) {
            if (is_json_mode) {
                // Verify json_output is 1 before adding to the JSON data object
                if (meta->json_output == 1) {
                    switch (meta->type) {
                        case TYPE_NUM: {
                            uint32_t val = 0;
                            if (data_len <= 4) {
                                for (size_t i = 0; i < data_len; i++) {
                                    val = (val << 8) | payload[i];
                                }
                            }
                            cJSON_AddItemToObject(data_obj, meta->name, cJSON_CreateNumber(val));
                            break;
                        }
                        case TYPE_HEX: {
                            char hex_str[2048] = "0x";
                            size_t offset = 2;
                            for (size_t i = 0; i < data_len && offset < sizeof(hex_str) - 2; i++) {
                                snprintf(hex_str + offset, sizeof(hex_str) - offset, "%02X", payload[i]);
                                offset += 2;
                            }
                            cJSON_AddItemToObject(data_obj, meta->name, cJSON_CreateString(hex_str));
                            break;
                        }
                        case TYPE_STRING: {
                            cJSON_AddItemToObject(data_obj, meta->name, cJSON_CreateString((char *)payload));
                            break;
                        }
                    }
                }
            } else {
                // Screen output mode (when output_file is NULL)
                printf("[Index %3u] %-25s : ", meta->index, meta->name);
                switch (meta->type) {
                    case TYPE_NUM: {
                        uint32_t val = 0;
                        if (data_len <= 4) {
                            for (size_t i = 0; i < data_len; i++) {
                                val = (val << 8) | payload[i];
                            }
                        }
                        printf("%u (num)\n", val);
                        break;
                    }
                    case TYPE_HEX: {
                        printf("0x");
                        for (size_t i = 0; i < data_len; i++) printf("%02X", payload[i]);
                        printf(" (hex)\n");
                        break;
                    }
                    case TYPE_STRING: {
                        printf("\"%s\" (string)\n", (char *)payload);
                        break;
                    }
                }
            }
        } else {
            // Unmapped tag handling
            if (!is_json_mode) {
                printf("[Index %3u] Unmapped Tag           : 0x", data_index);
                for (size_t i = 0; i < data_len; i++) {
                    printf("%02X", payload[i]);
                }
                printf(" (Hex Fallback)\n");
            }
        }

        free(payload);
    }

    close(fd);

    // If writing JSON mode, serialize the cJSON structure and write to file
    if (is_json_mode) {
		snprintf (BoxLabel2DCode,sizeof(BoxLabel2DCode),"%s+%s+%s+%s",sap,sn,mac,ctn);
		snprintf (ProductLabel2DCode,sizeof(ProductLabel2DCode),"%s+%s+%s",sap,sn,mac);
		snprintf (InstallerLabelQRCode,sizeof(InstallerLabelQRCode),"%s+%s+%s",sn,mac,ctn);
		cJSON_AddItemToObject(label_obj, "BoxLabel2DCode", cJSON_CreateString(BoxLabel2DCode));
		cJSON_AddItemToObject(label_obj, "ProductLabel2DCode", cJSON_CreateString(ProductLabel2DCode));
		cJSON_AddItemToObject(label_obj, "InstallerLabelQRCode", cJSON_CreateString(InstallerLabelQRCode));
        char *json_string = cJSON_Print(root);
        if (json_string) {
            FILE *fout = fopen(output_file, "w");
            if (fout) {
                fprintf(fout, "%s\n", json_string);
                fclose(fout);
                printf("Successfully wrote JSON data to: %s\n", output_file);
            } else {
                perror("Failed to open output file for writing JSON");
            }
            free(json_string);
        }
        cJSON_Delete(root); // Free memory allocated by cJSON
    } else {
        printf("----------------------------------------\n");
    }
	
	if (strlen(sap) > 0 && strlen (mac) && strlen(sn)) {
		printf(ANSI_COLOR_GREEN   "Get Meta data successfully!!"   ANSI_COLOR_RESET "\n");
		exit(OKSTATUS);
	} else {
		printf(ANSI_COLOR_RED     "Invalid File Data Format!"     ANSI_COLOR_RESET "\n");
		exit(EINVALIDDATA);
	}

    return 0;
}