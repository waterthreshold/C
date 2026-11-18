# Compiler and flags
CC = aarch64-linux-gnu-gcc
CFLAGS = -Wall -Wextra -O2

# Target executable and installation directory
TARGET = UploadFW.cgi
INSTALL_DIR = ../www/cgi-bin

# Default target
all: $(TARGET)
	@if [ ! -d "$(INSTALL_DIR)" ]; then \
		echo "Directory $(INSTALL_DIR) does not exist. Creating it..."; \
		mkdir -p "$(INSTALL_DIR)"; \
	fi
	@echo "Installing $(TARGET) to $(INSTALL_DIR)/..."
	@cp -f $(TARGET) $(INSTALL_DIR)/
	@chmod +x $(INSTALL_DIR)/$(TARGET)
	@echo "Installation complete."

# Rule to build the executable from the source file
$(TARGET): UploadFW.c
	$(CC) $(CFLAGS) UploadFW.c -o $(TARGET)

# Clean up build artifacts
clean:
	rm -f $(TARGET) *.o

# Declare phony targets
.PHONY: all clean