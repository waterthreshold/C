###########################################################
## History:
##    2023/2/9 - [Wenjing Zhang] Create
##
## Copyright (c) 2023 Ambarella International LP
##
## This file and its contents ("Software") are protected by intellectual
## property rights including, without limitation, U.S. and/or foreign
## copyrights. This Software is also the confidential and proprietary
## information of Ambarella International LP and its licensors. You may not use, reproduce,
## disclose, distribute, modify, or otherwise prepare derivative works of this
## Software or any portion thereof except pursuant to a signed license agreement
## or nondisclosure agreement with Ambarella International LP or its authorized affiliates.
## In the absence of such an agreement, you agree to promptly notify and return
## this Software to Ambarella International LP
##
## THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
## INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF NON-INFRINGEMENT,
## MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
## IN NO EVENT SHALL AMBARELLA INTERNATIONAL LP OR ITS AFFILIATES BE LIABLE FOR ANY DIRECT,
## INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; COMPUTER FAILURE OR MALFUNCTION; OR BUSINESS
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.
###########################################################

#DEPS(amba.mk) prebuild-file(jobserver): unselect

PACKAGE_NAME = file

INSTALL_TODIR_sbin = usr/sbin/* /usr/sbin
INSTALL_TODIR_misc =  usr/local/share/misc/magic.mgc /usr/local/share/misc/
INSTALL_TODIR_lib = usr/lib/libmagic.so.1.0.0 /usr/lib
.PHONY: all clean install

all:
	@echo "Build $(PACKAGE_NAME) Done."

include $(ENV_MAKE_DIR)/inc.ins.mk

clean:
	@echo "Clean $(PACKAGE_NAME) Done."

install: install_todir_sbin install_todir_misc install_todir_lib
	@-ln -sf $(ENV_INS_ROOT)/usr/lib/libmagic.so.1.0.0  $(ENV_INS_ROOT)/usr/lib/libmagic.so.1	
	@-ln -sf $(ENV_INS_ROOT)/usr/lib/libmagic.so.1 $(ENV_INS_ROOT)/usr/lib/libmagic.so



