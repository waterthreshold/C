#DEPS(amba.mk) eepromtool(jobserver): &&??generic-heade  &&?? prebuild-cjson &&??app-logger

PACKAGE_NAME = eeprom_tool
PACKAGE_DEPS = generic-header cjson
BIN_NAME = eeprom_tool
INSTALL_TODIR_bin =  $(BIN_TARGETS) fakeroot/usr/local/bin/* /usr/local/bin


.PHONY: all clean install

all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.app.mk

eeprom_tool-srcs =eeprom_traverse.c eeprom_info.c
eeprom_tool-ldflags ?= -L$(ENV_DEP_ROOT)/usr/lib -lcjson
eeprom_tool-cflags  ?= -I$(ENV_DEP_ROOT)/usr/include/cjson
$(call set_flags,CFLAGS,$(eeprom_tool-srcs),$(eeprom_tool-cflags))
$(eval $(call add-bin-build,eeprom_tool,$(eeprom_tool-srcs),$(eeprom_tool-ldflags)))


all: $(BIN_TARGETS)

clean: clean_objs
	@-rm -f $(BIN_TARGETS)
	@-rm -f $(ENV_DEP_ROOT)/usr/local/bin/dump_BoschMeta.sh   $(ENV_DEP_ROOT)/usr/local/bin/stm32mcu_tool.sh 
	@echo "Clean $(PACKAGE_NAME) Done."


install: install_todir_bin 
	