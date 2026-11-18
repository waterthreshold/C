###########################################################
## History:
##    2022/07/07 - [Jing Leng] Create
##
## Copyright (c) 2022 Ambarella International LP
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

#DEPS(amba.mk) cec_heaterd(jobserver %): &&??generic-header


PACKAGE_NAME = cec_heaterd
PACKAGE_DEPS = generic-header

INSTALL_BINARIES = usr/local/bin/*

.PHONY: all clean install

include $(ENV_MAKE_DIR)/inc.app.mk
cec_heaterd-srcs = heater_simulate_daemon.c
$(eval $(call add-bin-build,cec_heaterd,$(BoschDriverAPI_example-srcs)))

all: $(BIN_TARGETS)

clean: clean_objs
	@rm -f  $(BIN_TARGETS)
	@rm $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/syslogd.service
	@rm $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/cec_heaterd.service	
	@echo "Clean $(PACKAGE_NAME) Done."
	
install: install_bins
	@mkdir -p $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants
	@ln -sf usr/lib/systemd/system/syslogd.service $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/syslogd.service
	@ln -sf usr/lib/systemd/system/cec_heaterd.service $(ENV_INS_ROOT)/etc/systemd/system/multi-user.target.wants/cec_heaterd.service