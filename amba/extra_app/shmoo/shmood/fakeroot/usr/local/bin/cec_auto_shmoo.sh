#!/bin/sh
trigger_wdt(){
	sync
	echo 1 > /proc/chicony_wdt/enable
	echo 10000 > /proc/chicony_wdt/period
}
valid_log_available(){
	
	if [ "$1" = "read" ]; then
		LEGAL_COUNT=`cat $2 | grep "rdq offset boundary is" | wc -l`
	elif [ "$1" = "write" ]; then 
		LEGAL_COUNT=`cat $2 | grep "wdq offset boundary is" | wc -l`
	fi
	
	[ $LEGAL_COUNT -eq 3 ] && return 0 || return 1 
	
}

recoard_shmoo_data(){
	mode="$1"
	LOGPATH="$2"
	[ -e "${LOGPATH}" ] && rm "${LOGPATH}"
	if [ "$mode" = "read" ]; then
		for i in `seq 1 3`
		do
			ddrc_v2 --offset rdq -d -1  > /tmp/r_neg	
			ddrc_v2 --offset rdq -d +1  > /tmp/r_pos	
			# r_neg=`cat /tmp/r_neg | sed 's/Testing rdq negative offset: //g' | awk '{print $NF}'`
			# r_pos=`cat /tmp/r_pos | sed 's/Testing rdq positive offset: //g' | awk '{print $NF}'`
			r_neg=`cat /tmp/r_neg | grep -oE -- '-[0-9]+' | tail -n1`
			r_pos=`cat /tmp/r_pos | grep -oE -- '\+[0-9]+' | tail -n1`
			cat /tmp/r_neg /tmp/r_pos  >> "${LOGPATH}"
			printf "\nrdq offset boundary is [%d,%d]" ${r_neg} ${r_pos} >>  "${LOGPATH}"
			# ddrc_v2 --offset rdq -d -1  >> "${MYLOGDIR}/${log_name}"
			# ddrc_v2 --offset rdq -d +1  >> "${MYLOGDIR}/${log_name}"
		done
	elif [ "$mode" = "write" ]; then
		for i in `seq 1 3`
		do
			ddrc_v2 --offset wdq  >> "${LOGPATH}"
		done 
	fi
}
probe_next_bst(){
	while IFS= read -r line; do
	if echo "$line" | grep -q "term" && echo $line | grep -q "ds"; then
read term ds <<EOF
	$(echo $line | sed -n 's/.*term\([0-9]*\)_ds\([0-9]*\)_.*/\1 \2/p')
EOF
		if [ ! -e "$ROOTDIR/${DEVICE_NAME}/read/${TEMP}/${DEVICE_NAME}_term${term}-ds${ds}.log" ]; then 
			echo "$line"
			break
		elif  ! valid_log_available "read" "$ROOTDIR/${DEVICE_NAME}/read/${TEMP}/${DEVICE_NAME}_term${term}-ds${ds}.log"; then 
			echo "$line"
			break
		fi
	elif echo "$line" | grep -q "pdds"  && echo "$line" | grep -q "odt"; then
read pdds dds odt <<EOF
$(echo $line | sed -n 's/.*pdds\([0-9]*\)_dds\([0-9]*\)_odt\([0-9]*\)_.*/\1 \2 \3/p')
EOF
		# WRITE_QUANTITY=$(( WRITE_QUANTITY + 1))
		if [ ! -e "$ROOTDIR/${DEVICE_NAME}/write/${TEMP}/${DEVICE_NAME}_pdds${pdds}-dds${dds}-odt${odt}.log" ]; then 
			# HIGH_FLAG=1
			# HIGH_WRITE_FAILED=$((HIGH_WRITE_FAILED + 1))
			echo "$line"
			break
		elif ! valid_log_available "write" "$ROOTDIR/${DEVICE_NAME}/write/${TEMP}/${DEVICE_NAME}_pdds${pdds}-dds${dds}-odt${odt}.log"; then 
			echo "$line"
			break
		fi
	fi
done < "${ROOTDIR}/Progress.txt"
}
#bstfw
##
#`hostname`
#|_ read
#	|_high	
#		\_xx log
#		\_xxlog
#	|_low
#		\_xx log
#		\_xxlog
#|_write
#	|_high	
#		\_xx log
#		\_xxlog
#	|_low
#		\_xx log
#		\_xxlog

# Main Section
modprobe ambdram_statis

DEVICE_NAME=`hostname`

TEMP="${1}"
REMOTE_HOST_IP="`jq -r '.static.host' /etc/shmoo.json`"
ROOTDIR=`jq -r '.profile_dir' /etc/shmoo.json`
CURRENTRUNBST="${ROOTDIR}/${TEMP}"
MYLOGDIR="${ROOTDIR}/${DEVICE_NAME}"

if [ -z "$ROOTDIR" ] || [ "$ROOTDIR" = "null" ]; then
	ROOTDIR="/root"
fi
[ ! -d "${MYLOGDIR}" ] && mkdir "${MYLOGDIR}"

[ -z "${TEMP}" ] && echo  "Must one paramater [high|low|normal]" && exit 1

if [ ! -e "$CURRENTRUNBST" ]; then
	upgrade_partition  -q -b 1 -p /dev/mmcblk0p1 "${ROOTDIR}/bst_fw/`sed -n '1p' ${ROOTDIR}/Progress.txt`bst.bin" 
	echo "`sed -n '1p' ${ROOTDIR}/Progress.txt`" > "$CURRENTRUNBST" 
	sync
	trigger_wdt
	exit 0
fi
log_name="${DEVICE_NAME}.log" 
if grep -q "term" ${CURRENTRUNBST} && grep -q "ds" ${CURRENTRUNBST}; then
read term ds <<EOF
$(cat ${CURRENTRUNBST} | sed -n 's/.*term\([0-9]*\)_ds\([0-9]*\)_.*/\1 \2/p')
EOF
   echo "read term:${term} ds${ds}"
   log_name="${DEVICE_NAME}_term${term}-ds${ds}.log"
   MYLOGDIR="${MYLOGDIR}/read/${TEMP}"
   [ ! -d ${MYLOGDIR} ] && mkdir -p ${MYLOGDIR}
   # [ -e "${MYLOGDIR}/${log_name}" ] && rm "${MYLOGDIR}/${log_name}" && touch "${MYLOGDIR}/${log_name}"
    if [ ! -e "${MYLOGDIR}/${log_name}" ]; then
		recoard_shmoo_data "read" "${MYLOGDIR}/${log_name}"
	elif ! valid_log_available "read" "${MYLOGDIR}/${log_name}"; then
		recoard_shmoo_data "read" "${MYLOGDIR}/${log_name}"
	fi 
	
elif grep -q "pdds" ${CURRENTRUNBST} && grep -q "odt" ${CURRENTRUNBST} ; then
read pdds dds odt <<EOF
$(cat ${CURRENTRUNBST} | sed -n 's/.*pdds\([0-9]*\)_dds\([0-9]*\)_odt\([0-9]*\)_.*/\1 \2 \3/p')
EOF
	echo "write pdds:${pdds} dds:${dds} odt:${odt}"
	log_name="${DEVICE_NAME}_pdds${pdds}-dds${dds}-odt${odt}.log"
	MYLOGDIR="${MYLOGDIR}/write/${TEMP}"
   [ ! -d ${MYLOGDIR} ] && mkdir -p ${MYLOGDIR}
   #[ -e "${MYLOGDIR}/${log_name}" ] && rm "${MYLOGDIR}/${log_name}" && touch "${MYLOGDIR}/${log_name}"
	if [ -e "${MYLOGDIR}/${log_name}" ]; then
		recoard_shmoo_data "write" "${MYLOGDIR}/${log_name}"
	elif ! valid_log_available "write" "${MYLOGDIR}/${log_name}"; then 
		recoard_shmoo_data "write" "${MYLOGDIR}/${log_name}"
	fi
	
	# for i in `seq 1 3`
	# do
	# ddrc_v2 --offset wdq  >> "${MYLOGDIR}/${log_name}"
	# done 
fi
# NEXT_PROGRESS=$(sed -n "/`cat ${CURRENTRUNBST}`/{n;p;}" /root/Progress.txt)
NEXT_PROGRESS="`probe_next_bst`"
if [ "${NEXT_PROGRESS}" = "" ]; then 
	echo "File read done!!" 
	echo "" > "${ROOTDIR}/${TEMP}"
	touch "${ROOTDIR}/${TEMP}_flag" 
	#rm ${CURRENTRUNBST}
fi
if [ -e "${ROOTDIR}/high_flag" ] && [ -e "${ROOTDIR}/low_flag" ]; then
	test_logger -p 514 -r ${REMOTE_HOST_IP} "${DEVICE_NAME} shmoo test done!!"
	/usr/local/bin/7zz a "${ROOTDIR}/${DEVICE_NAME}.7z" ${ROOTDIR}/${DEVICE_NAME}
	[ $? -eq 0 ] && curl -F "file=@${ROOTDIR}/${DEVICE_NAME}.7z" "http://${REMOTE_HOST_IP}/shmoo_data/"
	sync
	systemctl disable shmood
	exit 0
fi 
	
FW_NAME="${NEXT_PROGRESS}bst.bin" 

UPLOAD_FILE="${ROOTDIR}/bst_fw/${FW_NAME}"
# upgrade_partition  -q -b 1 -p /dev/mmcblk0p1  "$UPLOAD_FILE" 
echo 0 > /sys/block/mmcblk0boot0/force_ro
dd if=/dev/zero of=/dev/mmcblk0boot0
sleep 0.3
upgrade_partition -q  -p /dev/mmcblk0boot0 "$UPLOAD_FILE"
if [ $? -eq 0 ]; then
	
	echo ${NEXT_PROGRESS} > ${CURRENTRUNBST}
	echo "BST Firware ${UPLOAD_FILE} upgrade done" > /dev/kmsg
	sync
	sleep 1 
	trigger_wdt
else 
	echo "FW: ${UPLOAD_FILE} upgrade_partition failed" > /dev/kmsg
fi 