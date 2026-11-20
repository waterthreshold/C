# Compiler and flags
CC = aarch64-linux-gnu-gcc
CFLAGS = -Wall -Wextra -O2

# Target executable and installation directory
TARGET = test_resetbtnd

# Default target
$(TARGET): test_Factoryreset.c
	$(CC) $(CFLAGS) $^ -o $(TARGET)

# Clean up build artifacts
clean:
	rm -f $(TARGET) *.o

# Declare phony targets
.PHONY: all clean
