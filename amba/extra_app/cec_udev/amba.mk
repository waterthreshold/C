#DEPS(amba.mk) testudev(jobserver): &&??generic-header  &&?? prebuild-systemd

PACKAGE_NAME = udev_monitor
PACKAGE_DEPS = generic-header 
BIN_NAME = udev_monitor
INSTALL_TODIR_bin =  $(BIN_TARGETS)  /usr/local/bin


.PHONY: all clean install

all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

udev_monitor-srcs = udev_monitor.c
udev_monitor-ldflags ?= -L$(ENV_DEP_ROOT)/usr/lib -ludev
$(eval $(call add-bin-build,udev_monitor,$(udev_monitor-srcs),$(udev_monitor-ldflags)))


all: $(BIN_TARGETS)

clean: clean_objs
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin  
	
