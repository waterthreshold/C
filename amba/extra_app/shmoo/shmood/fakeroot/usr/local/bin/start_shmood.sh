#!/bin/sh
[ ! -e "/etc/shmoo.json" ] && echo "/etc/shmoo.json does not exist!!" && exit 1 
REMOTE_HOST_IP="`jq -r '.static.host' /etc/shmoo.json`"
ROOTDIR="`jq -r '.profile_dir' /etc/shmoo.json`"
ROOTDIR=${ROOTDIR-/root}
HOSTNAME=`hostname`
[ ! -d "${ROOTDIR}" ] && mkdir -p ${ROOTDIR}
trigger_wdt(){
	echo 1 > /proc/chicony_wdt/enable
	echo 10000 > /proc/chicony_wdt/period
}

# CURRENTRUNBST=/root/currentbst
/usr/local/bin/shmood &
# /usr/local/bin/receiver &

if [ -e "${ROOTDIR}/high_flag" ] && [ -e "${ROOTDIR}/low_flag" ]; then 
	test_logger -p 514 -r ${REMOTE_HOST_IP} "Bootup But shmoo test all finish"
	# /usr/local/bin/7zz a "${ROOTDIR}/${HOSTNAME}.7z" ${ROOTDIR}/${HOSTNAME}
	# [ $? -eq 0 ] && curl -F "file=@${ROOTDIR}/${HOSTNAME}.7z" "http://${REMOTE_HOST_IP}/shmoo_data/"
	killall shmood
	exit 0
# elif  [ -e "/root/high" ]; then 
	# test_logger -p 514 -r ${REMOTE_HOST_IP} "Bootup: High temp test done. wait chamber to down to `jq -r '.static.low' /etc/shmoo.json`"
	
# elif [ -e "/root/low" ]; then
	# test_logger -p 514 -r ${REMOTE_HOST_IP} "Bootup: High temp test done. wait chamber to climb to `jq -r '.static.high' /etc/shmoo.json`"
	
fi
if [ ! -e "$ROOTDIR/Progress.txt" ] && [ ! -d "${ROOTDIR}" ]; then 
	curl "http://${REMOTE_HOST_IP}/shmoo_data/bst.zip" -o "${ROOTDIR}/bst.zip"
	[ $? -eq 0 ] && unzip -d "${ROOTDIR}" "${ROOTDIR}/bst.zip"
fi
# if [ ! -e ${CURRENTRUNBST} ]; then
	# echo "`hostname` first shmoo run" > /dev/kmsg
	# UPLOAD_FILE="/root/bst_fw/`sed -n '1p' /root/Progress.txt`bst.bin"
	# upgrade_partition  -q -b 1 -p /dev/mmcblk0p1  "$UPLOAD_FILE" 
	# if [ $? -eq 0 ]; then
	
		# echo "`sed -n '1p' /root/Progress.txt`" > ${CURRENTRUNBST}
		# echo "BST Firware `cat ${CURRENTRUNBST}` upgrade done" > /dev/kmsg
		# sync
		# sleep 1 
		# trigger_wdt
	# fi
# else 
	# test_logger -p 514 -r ${REMOTE_HOST_IP}  "`hostname` run BST FW:`cat /root/currentbst`"
# fi 

sleep 1
echo "Start Loading"
/usr/local/bin/cec_shmoo_loading.sh -c "/etc/shmoo.json"