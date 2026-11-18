#!/bin/sh
cat /etc/fw_version
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
echo "CPU:${CPU_LOADING} %"
MEMFREEITEM=`cat /proc/meminfo | grep MemFree:`
FREE_MEM=`echo "${MEMFREEITEM// /}" | cut -d: -f 2`
echo "FREE_MEM:`echo "${FREE_MEM:0:-2} / 1024" | bc`MB" 
echo "uptime: `uptime | cut -d, -f 1`"
VP_IDLE=$(cavalry_top -b -n 1 -c 1 | grep "VP IDLE" | sed -E 's/.* ([0-9]+\.[0-9]+)%.*/\1/')
VP_USAGE=$(echo "100 - ${VP_IDLE}" | bc) 
VP_USAGE=`printf %.1f ${VP_USAGE}`
echo "VP:${VP_USAGE}"
echo -e "\n\n"
sleep ${SLEEPTIME}
done