#!/bin/sh
source /www/cgi-bin/global.sh
echo -e  "Content-type: text/plain\n"
echo -n "cam_num=${cam_num}&"
ASCII_A=65
for  i in `seq 0 $(( cam_num - 1))`; 
do	
	[ `cat /proc/cg5251tc_mc${i}/als_enable` -ne 1  ] && echo 1 > /proc/cg5251tc_mc${i}/als_enable
	#ASCII=$(( ASCII_A + i ))
	#ASCII_CHAR=$(printf "\x`printf "%x" $ASCII`")
	RESULT=$(cat /proc/cg5251tc_mc${i}/als_lux_raw)
	# RESULT=${RESULT//LUX:}
	echo -n "cam${i}_lux=${RESULT}&"
done