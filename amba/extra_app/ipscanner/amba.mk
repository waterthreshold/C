#DEPS(amba.mk) ipscanner(jobserver): &&??generic-heade

PACKAGE_NAME = ipscanner
PACKAGE_DEPS = generic-header
BIN_NAME = ipscanner
INSTALL_TODIR_service = ipscanner.service /usr/lib/systemd/system
INSTALL_TODIR_bin =  $(BIN_TARGETS) /usr/local/bin
include $(ENV_MAKE_DIR)/inc.env.mk

.PHONY: all clean install


all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

all: $(BIN_TARGETS)

clean: clean_objs
	@-rm -f $(BIN_TARGETS)
	@-rm -f $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/ipscanner.service
	@-rm -f  $(ENV_INS_ROOT)/usr/lib/systemd/system/ipscanner.service
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin install_todir_service
	@ln -sf  ipscanner.service  $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/ipscanner.service
