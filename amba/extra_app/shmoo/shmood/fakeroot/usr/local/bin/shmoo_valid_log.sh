#!/bin/sh
# ROOTDIR=`jq -r '.profile_dir' /etc/shmoo.json`
ROOTDIR="$1"
ROOTDIR=${ROOTDIR-"/root"}
HOSTNAME="`hostname`"

valid_log_available(){
	if [ "$1" = "read" ]; then
		LEGAL_COUNT=`cat $2 | grep "rdq offset boundary is" | wc -l`
	elif [ "$1" = "write" ]; then 
		LEGAL_COUNT=`cat $2 | grep "wdq offset boundary is" | wc -l`
	fi
	
	[ $LEGAL_COUNT -eq 3 ] && return 0 || return 1 	
}

[ ! -d "$ROOTDIR" ] && echo "$ROOTDIR not exist!!" && exit 1  
HIGH_FLAG=0
LOW_FLAG=0
WRITE_QUANTITY=0
READ_QUANTITY=0
HIGH_WRITE_FAILED=0
HIGH_READ_QUANTITY=0

LOW_WRITE_FAILED=0
LOW_READ_FAILED=0
echo "High:"
while IFS= read -r line; do
	if echo "$line" | grep -q "term" && echo $line | grep -q "ds" ; then
read term ds <<EOF
	$(echo $line | sed -n 's/.*term\([0-9]*\)_ds\([0-9]*\)_.*/\1 \2/p')
EOF
		READ_QUANTITY=$(( READ_QUANTITY + 1 ))
		if [ ! -e "$ROOTDIR/${HOSTNAME}/read/high/${HOSTNAME}_term${term}-ds${ds}.log" ]; then 
			HIGH_FLAG=1
			HIGH_READ_FAILED=$(( HIGH_READ_FAILED + 1 ))
			echo "$ROOTDIR/${HOSTNAME}/read/high/${HOSTNAME}_term${term}-ds${ds}.log not exist"
		elif  ! valid_log_available "read" "$ROOTDIR/${HOSTNAME}/read//high/${HOSTNAME}_term${term}-ds${ds}.log"; then 
			echo "$ROOTDIR/${HOSTNAME}/read/high/${HOSTNAME}_term${term}-ds${ds}.log Not complete!!"
			HIGH_FLAG=
			HIGH_READ_FAILED=$(( HIGH_READ_FAILED + 1 ))
		fi
	elif echo "$line" | grep -q "pdds"  && echo "$line" | grep -q "odt"; then
read pdds dds odt <<EOF
$(echo $line | sed -n 's/.*pdds\([0-9]*\)_dds\([0-9]*\)_odt\([0-9]*\)_.*/\1 \2 \3/p')
EOF
		WRITE_QUANTITY=$(( WRITE_QUANTITY + 1))
		if [ ! -e "$ROOTDIR/${HOSTNAME}/write/high/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log" ]; then 
			HIGH_FLAG=1
			HIGH_WRITE_FAILED=$((HIGH_WRITE_FAILED + 1))
			echo "$ROOTDIR/${HOSTNAME}/write/high/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log not exist"
		elif ! valid_log_available "write" "$ROOTDIR/${HOSTNAME}/write/high/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log"; then 
			echo "$ROOTDIR/${HOSTNAME}/write/high/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log Not complete!!"
			HIGH_FLAG=1
			HIGH_WRITE_FAILED=$((HIGH_WRITE_FAILED + 1))
		fi
	fi
done < "${ROOTDIR}/Progress.txt"
if [ $HIGH_FLAG  -eq 0 ]; then
	[ ! -e "${ROOTDIR}/high_flag" ] && touch "${ROOTDIR}/high_flag"
	echo "high sucessfully"
fi 


echo "Low:"
while IFS= read -r line; do
	if echo "$line" | grep -q "term" && echo $line | grep -q "ds" ; then
read term ds <<EOF
	$(echo $line | sed -n 's/.*term\([0-9]*\)_ds\([0-9]*\)_.*/\1 \2/p')
EOF
		if [ ! -e "$ROOTDIR/${HOSTNAME}/read/low/${HOSTNAME}_term${term}-ds${ds}.log" ]; then 
			LOW_FLAG=1
			LOW_READ_FAILED=$((LOW_READ_FAILED + 1))
			echo "$ROOTDIR/${HOSTNAME}/read/low/${HOSTNAME}_term${term}-ds${ds}.log not exist"
		elif  ! valid_log_available "read" "$ROOTDIR/${HOSTNAME}/read/low/${HOSTNAME}_term${term}-ds${ds}.log"; then 
			echo "$ROOTDIR/${HOSTNAME}/read/low/${HOSTNAME}_term${term}-ds${ds}.log Not complete!!"
			LOW_FLAG=1
			LOW_READ_FAILED=$((LOW_READ_FAILED + 1))
		fi
	elif echo "$line" | grep -q "pdds" && echo "$line" | grep -q "odt"; then
read pdds dds odt <<EOF
$(echo $line | sed -n 's/.*pdds\([0-9]*\)_dds\([0-9]*\)_odt\([0-9]*\)_.*/\1 \2 \3/p')
EOF
		if [ ! -e "$ROOTDIR/${HOSTNAME}/write/low/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log" ]; then 
			LOW_FLAG=1
			LOW_WRITE_FAILED=$((LOW_WRITE_FAILED + 1))
			echo "$ROOTDIR/${HOSTNAME}/write/low/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log not exist"
		elif  ! valid_log_available "write" "$ROOTDIR/${HOSTNAME}/write/low/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log"; then 
			echo "$ROOTDIR/${HOSTNAME}/write/low/${HOSTNAME}_pdds${pdds}-dds${dds}-odt${odt}.log Not complete!!"
			LOW_FLAG=1
			LOW_WRITE_FAILED=$((LOW_WRITE_FAILED + 1))
		fi
	fi
done < ${ROOTDIR}/Progress.txt
if [ $LOW_FLAG  -eq 0 ]; then
	[ ! -e "${ROOTDIR}/low_flag" ] && touch "${ROOTDIR}/low_flag"
	echo "low sucessfully"
fi 
echo "----------------------------------------------------------------"
echo "high read: $(( READ_QUANTITY - HIGH_READ_FAILED )) / ${READ_QUANTITY}"
echo "high write: $(( WRITE_QUANTITY - HIGH_WRITE_FAILED)) / ${WRITE_QUANTITY}"
echo "low read: $(( READ_QUANTITY - LOW_READ_FAILED)) / ${READ_QUANTITY}"
echo "low write: $(( WRITE_QUANTITY - LOW_WRITE_FAILED)) / ${WRITE_QUANTITY}"
echo "----------------------------------------------------------------"
