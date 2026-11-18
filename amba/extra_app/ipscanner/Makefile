# Compiler configuration (supports cross-compilation override via 'make CC=arm-linux-gnueabihf-gcc')
CROSS_COMPILE ?= aarch64-linux-gnu-

CC = $(CROSS_COMPILE)gcc
CFLAGS = -Wall -Wextra -O2

# Target executable name
TARGET = ipscanner

# Source and Object files
SRCS = ipscanner.c netlib.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c netlib.h
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
