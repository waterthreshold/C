#!/bin/sh
source ./global.sh
ret='0'
#0: Still Running 1: low finish 2: High finish 3. High / Low Finish

low_finish=`python -c 'print (1<<0)'`
high_finish=`python -c 'print (1<<1)'`

[ ! -e "/etc/shmoo.json" ]  && ret="-1" 
[ ! -e "/root/Progress.txt" ]  && ret='-2'
NOW_TEMP=`cat /sys/class/hwmon/hwmon0/temp1_input`
NOW_TEMP=$(( NOW_TEMP / 1000 ))
if [ "$NOW_TEMP" -ge "`jq -r '.static.high' /etc/shmoo.json`" ]; then 
	mode=high
elif [ "$NOW_TEMP" -le "`jq -r '.static.low' /etc/shmoo.json`" ]; then
	mode=low
else 
	mode=normal
fi

ROOTDIR="`/usr/local/bin/jq -r '.profile_dir' /etc/shmoo.json`"
ROOTDIR=${ROOTDIR-"/root"}
[ ! -e ${ROOTDIR}/${mode} ] && ret='-3'
if [ "$ret" != "0" ]; then 
	echo -e "Content-type: text/plain\n"
	echo -e "ret=$ret&mode=${mode}"
else
	total=`cat "$ROOTDIR/Progress.txt" | wc -l`
	
	
	num="$(grep -n -m 1 "`cat ${ROOTDIR}/${mode}`" ${ROOTDIR}/Progress.txt | cut -d: -f 1)"
	
	finish=0
	[ -e "${ROOTDIR}/high_flag" ] && finish=$(( finish + high_finish))
	[ -e "${ROOTDIR}/low_flag" ] && finish=$(( finish + low_finish))
	echo -e "Content-type: text/plain\n"
	bst=`cat "${ROOTDIR}/${mode}"`
	echo -e "ret=$ret&num=$num&total=${total}&mode=${mode}&finish=${finish}&bst=${bst}"
fi

