# Cross-compiler prefix
CROSS_COMPILE ?= aarch64-linux-gnu-
CC = $(CROSS_COMPILE)gcc

# Target binary name and source file
TARGET = camInfo
SRC = camInfo.c

# Compiler flags
# -Wall -Wextra: Enable useful compiler warnings
# -O2: Standard optimization level
CFLAGS = -Wall -Wextra -O2

# Optional: Uncomment and set SYSROOT if your toolchain needs a specific target rootfs
# SYSROOT = /path/to/your/aarch64/sysroot
# CFLAGS += --sysroot=$(SYSROOT)
# LDFLAGS += --sysroot=$(SYSROOT)

# Linker flags (if you need extra libraries later, e.g., -lpthread)
LDFLAGS =

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET) *.o