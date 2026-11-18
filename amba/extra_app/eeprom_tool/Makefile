# Default compiler (can be overridden via command line: make CC=aarch64-linux-gnu-gcc)
CC = aarch64-linux-gnu-gcc

# Compiler flags
CFLAGS = -Wall -Wextra -O2 -std=gnu99 -I/home/jeff/odm_cv5_larnaca2_Mirror_202607021749/ambarella/prebuild/oss/armv8-a/cjson/include
LDFLAGS = -L/home/jeff/odm_cv5_larnaca2_Mirror_202607021749/ambarella/prebuild/oss/armv8-a/cjson/usr/lib -lcjson

# Target binary name
TARGET = eeprom_tool

# Source file
SRCS = eeprom_traverse.c eeprom_info.c
OBJS = $(SRCS:.c=.o)
DEPS = eeprom_info.h

# Default rule
all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET) $(LDFLAGS)

# Generic rule to compile .c files into .o object files
%.o: %.c $(DEPS)
	$(CC) $(CFLAGS) -c $< -o $@

# Clean rule to remove compiled binaries
clean:
	rm -f $(TARGET) *.o

# Phony targets
.PHONY: all clean
