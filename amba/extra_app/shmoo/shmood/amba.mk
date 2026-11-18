#DEPS(amba.mk) shmood(jobserver): &&??receiverd &&??json-c &&??libshmoo &&??app-logger

PACKAGE_NAME = shmood
PACKAGE_DEPS = json-c libshmoo
BIN_NAME = shmood

INSTALL_TODIR_service =  fakeroot/usr/lib/systemd/system/shmood.service /usr/lib/systemd/system
INSTALL_TODIR_bin = $(BIN_TARGETS) fakeroot/usr/local/bin/* /usr/local/bin
INSTALL_TODIR_config = fakeroot/etc/shmoo.json /etc


.PHONY: all clean install


all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk
shmood-srcs =shmood.c
shmood-ldflags ?= -L$(ENV_DEP_ROOT)/usr/lib -ljson-c -lshmoo
$(eval $(call add-bin-build,shmood,$(shmood-srcs),$(shmood-ldflags)))

all: $(BIN_TARGETS)

clean: clean_objs
	@-rm -f $(ENV_INS_ROOT)/etc/shmoo.json
	@-rm -rf  $(ENV_INS_ROOT)/usr/lib/systemd/system/shmood.service
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin install_todir_service install_todir_config 
