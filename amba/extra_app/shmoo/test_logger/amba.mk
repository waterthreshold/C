#DEPS(amba.mk) app-logger(jobserver): &&??generic-header &&??libshmoo

PACKAGE_NAME = test_logger
PACKAGE_DEPS = generic-header libshmoo
BIN_NAME = test_logger
INSTALL_TODIR_bin =  $(BIN_TARGETS)  /usr/local/bin


.PHONY: all clean install

all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk
test_logger-srcs =test_logger.c
test_logger-ldflags ?= -L$(ENV_DEP_ROOT)/usr/lib -lshmoo
$(eval $(call add-bin-build,test_logger,$(test_logger-srcs),$(test_logger-ldflags)))

all: $(BIN_TARGETS)

clean: clean_objs


install: install_todir_bin 
	
