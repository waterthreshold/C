#!/bin/sh 
# run offset shmoo manually
#

[ ! -e "/etc/shmoo.json" ] && echo "Not exist /etc/shmoo.json" && exit 1
HIGH_TEMP=`jq -r '.static.high' /etc/shmoo.json`
LOW_TEMP=`jq -r '.static.low' /etc/shmoo.json`
DURATIONTIME=`jq -r '.static.max_duration_min' /etc/shmoo.json`
REMOTE_HOST_IP="`jq -r '.static.host' /etc/shmoo.json`"

DURATIONTIME=$(( DURATIONTIME * 60 ))
PROFILE_DIR=`jq -r '.profile_dir' /etc/shmoo.json`
PROFILE_DIR_H_R="${PROFILE_DIR}/offset/`hostname`/read/high/`hostname`_term6-ds4.log"
PROFILE_DIR_L_R="${PROFILE_DIR}/offset/`hostname`/read/low/`hostname`_term6-ds4.log"
PROFILE_DIR_H_W="${PROFILE_DIR}/offset/`hostname`/write/high/`hostname`_pdds5-dds6-odt4.log"
PROFILE_DIR_L_W="${PROFILE_DIR}/offset/`hostname`/write/low/`hostname`_pdds5-dds6-odt4.log"
mkdir -p "`dirname ${PROFILE_DIR_H_R}`" "`dirname ${PROFILE_DIR_L_R}`" "`dirname ${PROFILE_DIR_H_W}`" "`dirname ${PROFILE_DIR_L_W}`"
/usr/local/bin/cec_shmoo_loading.sh -s 
/usr/local/bin/cec_shmoo_loading.sh -c /etc/shmoo.json

STATUS_ABNORMAL=0
START_TIME=0
SLEEP_TIME=3 # const val

while [ 1 ]; do
	NOW_TEMP=`cat /sys/class/hwmon/hwmon0/temp1_input`
	NOW_TEMP=$(( NOW_TEMP / 1000 ))
	if [ $NOW_TEMP -ge "$HIGH_TEMP" ]; then
		STATUS_ABNORMAL=1
		[ $START_TIME -eq 0 ] && START_TIME=`date +%s`
	elif [ $NOW_TEMP -le "$LOW_TEMP" ]; then
		STATUS_ABNORMAL=2
		[ $START_TIME -eq 0 ] &&  START_TIME=`date +%s`
	else 
		STATUS_ABNORMAL=0
		START_TIME=0
	fi
	[ $STATUS_ABNORMAL -eq 0 ] && sleep ${SLEEP_TIME} && continue
	NOW_TIME=`date +%s`
	if [ $STATUS_ABNORMAL -ne 0 ]  &&  [ $(( NOW_TIME - START_TIME )) -gt  ${DURATIONTIME} ]; then 
		if [ $STATUS_ABNORMAL -eq 1 ]; then 
			echo "HIGH TEMPRATURE RECOAD data start !!"
			/usr/local/bin/cec_run_shmoo_test.sh -n 3 -f ${PROFILE_DIR_H_R} r
			/usr/local/bin/cec_run_shmoo_test.sh -n 3 -f ${PROFILE_DIR_H_W} w
			test_logger -p 514 -r ${REMOTE_HOST_IP} "[`hostname`] High temprature trigger"
			echo "HIGH TEMPRATURE RECOAD data done !!"
		elif [ $STATUS_ABNORMAL -eq 2 ]; then 
			echo "LOW TEMPRATURE RECOAD data start !!"
			/usr/local/bin/cec_run_shmoo_test.sh -n 3 -f ${PROFILE_DIR_L_R} r
			/usr/local/bin/cec_run_shmoo_test.sh -n 3 -f ${PROFILE_DIR_L_W} w
			test_logger -p 514 -r ${REMOTE_HOST_IP} "[`hostname`] low temprature trigger"
			echo "LOW TEMPRATURE RECOAD data  done!!"
		fi
		break
	fi
	
	sleep ${SLEEP_TIME}
done 
ZIP_NAME="`hostname`-offset.7z"
if [ -e "$PROFILE_DIR_H_R" ] && [ -e "$PROFILE_DIR_L_R" ] && [ -e "$PROFILE_DIR_H_W" ]  && [ -e "$PROFILE_DIR_L_W" ]; then
	echo "START TRANSFER OFFSET RESULT START!!"
	/usr/local/bin/7zz a "${PROFILE_DIR}/${ZIP_NAME}" "${PROFILE_DIR}/offset/`hostname`"
	[ $? -eq 0 ] && curl -F "file${PROFILE_DIR}/${ZIP_NAME}" "http://${REMOTE_HOST_IP}/shmoo_data/"
	echo "START TRANSFER OFFSET RESULT DONE!!"
fi 	
