#!/bin/sh
echo "version: `cat /etc/fw_version`"
date
echo -e "\n\n"
SLEEPTIME=5
while [ 1 ];
do
TEMP=`cat /sys/class/hwmon/hwmon0/temp1_input`
echo "Temprature: $((TEMP / 1000)) degree"
line=`top -n 1 -b | grep -m 1  CPU:`
usr=$(echo "$line" | sed -n 's/.* \([0-9.]*\)% usr.*/\1/p')
sys=$(echo "$line" | sed -n 's/.* \([0-9.]*\)% sys.*/\1/p')
CPU_LOADING=`echo ${usr} + ${sys} | bc` 
echo "CPU: ${CPU_LOADING} %"
MEMFREEITEM=`cat /proc/meminfo | grep MemFree:`
echo "${MEMFREEITEM// /}"
echo "uptime: `uptime | cut -d, -f 1`"
echo -e "\n\n"
sleep ${SLEEPTIME}
done