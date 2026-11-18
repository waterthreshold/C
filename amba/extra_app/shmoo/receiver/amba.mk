#DEPS(amba.mk) receiverd(jobserver): &&??generic-header

PACKAGE_NAME = receiver
PACKAGE_DEPS = generic-header
BIN_NAME = receiver
INSTALL_TODIR_service = receiver.service /usr/lib/systemd/system
INSTALL_TODIR_bin =  $(BIN_TARGETS) /usr/local/bin
include $(ENV_MAKE_DIR)/inc.env.mk

.PHONY: all clean install


all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

all: $(BIN_TARGETS)

clean: clean_objs
	@-rm -f $(BIN_TARGETS)
	@-rm -f  $(ENV_INS_ROOT)/usr/lib/systemd/system/receiver.service
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin install_todir_service
	