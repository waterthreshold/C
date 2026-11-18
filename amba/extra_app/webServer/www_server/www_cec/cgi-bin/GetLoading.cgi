#!/bin/sh
source ./global.sh

line=`top -n 1 -b | grep -m 1  CPU:`
usr=$(echo "$line" | sed -n 's/.* \([0-9.]*\)% usr.*/\1/p')
sys=$(echo "$line" | sed -n 's/.* \([0-9.]*\)% sys.*/\1/p')
CPU_LOADING=`echo ${usr} + ${sys} | bc` 
# echo "CPU:${CPU_LOADING} %"
MEMFREEITEM=`cat /proc/meminfo | grep MemFree:`
FREE_MEM=`echo "${MEMFREEITEM// /}" | cut -d: -f 2`
FREE_MEM_MB=`echo "${FREE_MEM:0:-2} / 1024" | bc`
# echo "FREE_MEM:`echo "${FREE_MEM:0:-2} / 1024" | bc`MB" 
# echo "uptime: `uptime | cut -d, -f 1`"
VP_IDLE=$(cavalry_top -b -n 1 -c 1 | grep "VP IDLE" | sed -E 's/.* ([0-9]+\.[0-9]+)%.*/\1/')
VP_USAGE=$(echo "100 - ${VP_IDLE}" | bc) 
VP_USAGE=`printf %.1f ${VP_USAGE}`
CONTENT=`echo "CPU=${CPU_LOADING}&VP=${VP_USAGE}&MEMFREE=${FREE_MEM_MB}"`
[ -e "/root/pot_value" ] && CONTENT=`echo "${CONTENT}&potval=$(cat /root/pot_value)"`
# echo "VP:${VP_USAGE}"
# echo -e "\n\n"
# sleep ${SLEEPTIME}
# done
echo -e  "Content-type: text/plain\n"
echo "$CONTENT"