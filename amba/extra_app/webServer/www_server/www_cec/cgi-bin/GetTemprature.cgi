#!/bin/sh
source ./global.sh
GPIO_HT_EN=61
echo -e  "Content-type: text/plain\n"
TEMP=`cat /sys/class/hwmon/hwmon0/temp1_input` 
TEMP=$((TEMP / 1000 ))
TEMP2=$(cat /sys/bus/iio/devices/iio:device0/in_voltage2_raw)
HT_EN=`amba_debug -g ${GPIO_HT_EN} | grep data | cut -d" " -f 2  | xargs printf %d`
echo "temp0=$TEMP&temp1=$TEMP2&HE_EN=${HT_EN}"