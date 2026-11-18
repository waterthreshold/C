#DEPS(amba.mk) cecscript(jobserver): 

PACKAGE_NAME = cecscript
SRC_DIR = "fakeroot/usr/local/bin"
OUT_DIR = $(ENV_INS_ROOT)/usr/local/bin
INSTALL_TODIR_bin =  $(BIN_TARGETS) /usr/local/bin
include $(ENV_MAKE_DIR)/inc.env.mk

.PHONY: all clean install


all:
	@for i in `ls -1 $(SRC_DIR)/`; do \
		if [ ! -x "$$i" ]; then \
			chmod +x "$(SRC_DIR)/$$i"; \
		fi && \
		cp -f  "$(SRC_DIR)/$$i" $(OUT_DIR)/$$i; \
	done
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.ins.mk

clean:
	@for i in `ls -1 $(SRC_DIR)/`; do \
		rm -f  $(OUT_DIR)/$$i; \
	done
	@echo "Clean $(PACKAGE_NAME) Done."

install: install_todir_bin