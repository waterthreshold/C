#DEPS(amba.mk) test_resetbtnd(jobserver): &&??generic-heade

PACKAGE_NAME = test_resetbtnd
PACKAGE_DEPS = generic-header
BIN_NAME = test_resetbtnd

INSTALL_TODIR_bin =  $(BIN_TARGETS) /usr/local/bin
include $(ENV_MAKE_DIR)/inc.env.mk

.PHONY: all clean install


all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

all: $(BIN_TARGETS)

clean: clean_objs
	@-rm -f $(BIN_TARGETS)
	
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin 