#DEPS(amba.mk) libshmoo(jobserver): &&??generic-header

PACKAGE_NAME = libshmoo
PACKAGE_DEPS = generic-header

SHMOO_SO_VER_MAJOR  := 0
SHMOO_SO_VER_MINOR  := 1
SHMOO_SO_VER_PATCH  := 0

LIBSO_NAME = libshmoo.so $(SHMOO_SO_VER_MAJOR) $(SHMOO_SO_VER_MINOR) $(SHMOO_SO_VER_PATCH)
INSTALL_HEADERS = logger.h utils.h 
INSTALL_TODIR_pkgconfig = libshmoo.pc /usr/lib/pkgconfig


.PHONY: all clean install

all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

all: $(LIB_TARGETS)

clean: clean_objs
	@-rm -f $(LIB_TARGETS)
	@echo "Clean $(PACKAGE_NAME) Done."

install: install_libs install_hdrs
