#ifndef EEPROM_TOOL_H
#define EEPROM_TOOL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif


typedef enum {
    TYPE_NUM,
    TYPE_HEX,
    TYPE_STRING
} TagType;

typedef struct {
    const char *name;
    uint16_t index;
    int json_output;
    TagType type;
} TagMeta;

// Lookup table based on your specification
#define OKSTATUS		(0)
enum
{
    EFILENOTEXIST = 1,
	EOUTFILEEIXST,
	EINVALIDDATA
};

#define ANSI_COLOR_RED     "\x1b[31m"
#define ANSI_COLOR_GREEN   "\x1b[32m"
#define ANSI_COLOR_RESET   "\x1b[0m"

#define TAG_TABLE_SIZE (sizeof(TAG_TABLE) / sizeof(TAG_TABLE[0]))
int show_info( char *source_path,  char *output_file) ;
void replace_charater(char *str, char src, char target);

#ifdef __cplusplus
}
#endif

#endif /* EEPROM_TOOL_H */