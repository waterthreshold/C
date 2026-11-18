#!/bin/sh
# mode 1 high -> low
# mode 2 low to _high
[ ! -e "/etc/shmoo.json" ] &&  echo "check /etc/shmoo.json" && exit 1

ROOTDIR="`jq -r '.profile_dir' /etc/shmoo.json`"
ROOTDIR=${ROOTDIR}/dynamic/`hostname`
mkdir -p ${ROOTDIR}
DURATIONTIME=`jq -r '.static.max_duration_min' /etc/shmoo.json`
REMOTE_HOST_IP="`jq -r '.static.host' /etc/shmoo.json`"
HIGH_TEMP=`jq -r '.static.high' /etc/shmoo.json`
LOW_TEMP=`jq -r '.static.low' /etc/shmoo.json`
DURATIONTIME=$(( DURATIONTIME * 60 ))
mode=$1
if [ $1 -eq 1 ]; then
FIRST_FILE_NAME=${ROOTDIR}/"$1_high2low.log"
FIRST_FILE_NAME_WDQ=${ROOTDIR}/"$1_high2low_w.log"
SECOND_FILE_NAME=${ROOTDIR}/"$1_low.log"
SECOND_FILE_NAME_WDQ=${ROOTDIR}/"$1_low_w.log"
elif [ $1 -eq 2 ]; then
FIRST_FILE_NAME=${ROOTDIR}/"$1_low2high.log"
SECOND_FILE_NAME=${ROOTDIR}/"$1_high.log"
FIRST_FILE_NAME_WDQ=${ROOTDIR}/"$1_low2high_w.log"
SECOND_FILE_NAME_WDQ=${ROOTDIR}/"$1_high_w.log"
else 
	echo "$0 <mode>[1|2] dynamic_shmoo.sh 1"
	exit 1
fi

/usr/local/bin/cec_shmoo_loading.sh -s 
/usr/local/bin/cec_shmoo_loading.sh -c /etc/shmoo.json
# ROOTDIR="/root"
echo 0 > /proc/ambarella/lp5adj 
rm /tmp/ddrcv2params
/usr/local/bin/cec_run_shmoo_test.sh -n 1 -f ${FIRST_FILE_NAME_WDQ} w
ddrc_v2 --adjust >  ${FIRST_FILE_NAME}  &

sleep ${DURATIONTIME}
# in the low temp


while  [ 1 ]; do
	NOW_TEMP=`cat /sys/class/hwmon/hwmon0/temp1_input`
	NOW_TEMP=$(( NOW_TEMP / 1000 ))
	if [ $mode -eq 1 ] && [ ${NOW_TEMP} -le "${LOW_TEMP}" ] ; then
		echo "high to low trigger "
		killall ddrc_v2
		break
	elif [ $mode -eq 2 ] && [ ${NOW_TEMP} -ge ${HIGH_TEMP} ]; then
		echo "low to high trigger"
		killall ddrc_v2	
		break
	fi
	sleep 1 
done
# echo "start recoard low"
rm /tmp/ddrcv2params 
# ddrc_v2 --offset wdq
/usr/local/bin/cec_run_shmoo_test.sh -n 1 -f ${SECOND_FILE_NAME_WDQ} w
ddrc_v2 --adjust >   ${SECOND_FILE_NAME} &
sleep ${DURATIONTIME}
killall ddrc_v2
touch $ROOTDIR/mode${mode}_finish

