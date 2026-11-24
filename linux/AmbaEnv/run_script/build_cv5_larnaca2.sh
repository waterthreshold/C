#!/bin/sh

BRANCHNAME='main'
GITSERVER='http://172.16.9.242:16888/Jeff_Chiang/odm_cv5_larnaca2_Mirror.git'
mkdir /sandbox
export PATH=$PATH:/usr/local/cortex-a76-2023.04-gcc12.2-linux5.15/bin
git lfs install
git clone ${GITSERVER} -b ${BRANCHNAME} /sandbox/odm_cv5_larnaca2_Mirror
cd /sandbox/odm_cv5_larnaca2_Mirror
cd ambarella/boards/cv5_larnaca2/
make ipcam_emmc_config
source ../../build/env/amba-build.env
make -j$(nporc)
FIRMWARE_NAME="`cat rootfs/default/etc/fw_version`-`git rev-parse --short HEAD`-`date +"%y%m%d_%H%M%S"`.bin"
[ ! -d "/amba_fw/cv5_larnaca2" ] && mkdir /amba_fw/cv5_larnaca2
cp "`find ../../out/amba_out/cv5_larnaca2/firmware/ -type f -name "*.bin" -exec du -b {} + | sort -nr | head -n 1 | awk '{print $2}'`"  "/amba_fw/cv5_larnaca2/${FIRMWARE_NAME}"     
