#DEPS(amba.mk) webserver(jobserver): generic-header  &&??prebuild-redis &&??www-upgrademodule

PACKAGE_NAME = webserver
PACKAGE_DEPS = generic-header prebuild-redis

INSTALL_TODIR_service = httpd.service /usr/lib/systemd/system
INSTALL_TODIR_bin =  fakeroot/usr/local/bin/* /usr/local/bin
INSTALL_TODIR_config = httpd.conf /etc
INSTALL_TODIR_www = www_cec/* /www
include $(ENV_MAKE_DIR)/inc.env.mk

.PHONY: all clean install


all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

all: $(BIN_TARGETS)

clean: clean_objs
	@-rm -f $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/httpd.service
	@-rm -f $(ENV_INS_ROOT)/etc/httpd.conf
	@-rm -rf  $(ENV_INS_ROOT)/www
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin install_todir_service install_todir_config install_todir_www
