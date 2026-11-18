#!/bin/sh
rmmod lefkosia_wdt
GPIO_XC6131_EN=136
GPIO_XC6131_WD=78

INTEVAL_WD=${1-2200}
BIAS=500
COUNT=0
SLEEPTIME=`printf "%.3f\n" $(echo "scale=3; ( ${INTEVAL_WD} - ${BIAS} ) / 2 / 1000" | bc -l)` # 925ms was critial point 2.2u captitor 900 ms more safe
echo "${SLEEPTIME}s as per duty cycle time..."
amba_debug -g ${GPIO_XC6131_WD} -d 0  
amba_debug -g ${GPIO_XC6131_EN} -d 0

while [ 1 ]; do
	amba_debug -g ${GPIO_XC6131_WD} -d 1
	sleep ${SLEEPTIME}
	amba_debug -g ${GPIO_XC6131_WD} -d 0
	sleep ${SLEEPTIME}
	COUNT=$(( COUNT + 1))
	if [ "$(( COUNT % 10 ))" -eq 0 ]; then
		echo "wdt count=${COUNT}" > /dev/kmsg
	fi
done 

# echo 1 > /proc/chicony_wdt/enable 
# echo 890 > /proc/chicony_wdt/period  # the device driver not mapping 925 ms  crital point in my perspective