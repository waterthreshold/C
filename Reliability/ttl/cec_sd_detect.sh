#!/bin/sh

if [ `ls /sys/class/mmc_host/mmc1/mmc1:* -1d  2>/dev/null | wc -l` -ne 0 ]; then  
	[ `mount|grep -E "/dev/mmcblk1.*"|awk -F" " "{print $3}" | wc -l` -gt 0 ] && echo "	 SD1. PASS" || echo "	 SD1. FAIL"
else
	echo "	 SD1. not inserted sd card !!"
fi
if [ `ls /sys/class/mmc_host/mmc2/mmc2:* -1d  2>/dev/null | wc -l` -ne 0 ]; then  
	[ `mount|grep -E "/dev/mmcblk2.*"|awk -F" " "{print $3}" | wc -l` -gt 0 ] && echo "	 SD2. PASS" || echo "	 SD2. FAIL"
else
	echo "	 SD2. not inserted sd card !!"
fi