#!/bin/sh
COUNT=1
FILE=""
MODE="rw"
## cec_run_shmoo_test.sh -n 1 -f rr11 r
## cec_run_shmoo_test.sh -n <run how many time> -f <redirect to file path> [mode r/w]
get_read(){
	
	for i in `seq 1 ${COUNT}`
	do
		if [ -z "$1" ]; then
			ddrc_v2 --offset rdq -d -1  
			ddrc_v2 --offset rdq -d +1
		else
			ddrc_v2 --offset rdq -d -1  > /tmp/r_neg #2>&1
			ddrc_v2 --offset rdq -d +1  > /tmp/r_pos #2>&1
			r_neg=`cat /tmp/r_neg | grep -oE -- '-[0-9]+' | tail -n1`
			r_pos=`cat /tmp/r_pos | grep -oE -- '\+[0-9]+' | tail -n1`
			cat /tmp/r_neg /tmp/r_pos  >> "${1}"
			printf "\nrdq offset boundary is [%d,%d]" ${r_neg} ${r_pos} >>  "${1}"
			# ddrc_v2 --offset rdq -d -1  2>&1 | tee -a "${1}"
			# ddrc_v2 --offset rdq -d +1  2>&1 | tee -a "${1}"

		fi
	done
}

get_write(){
	for i in `seq 1 ${COUNT}`
	do
		if [ -z "$1" ]; then	
			ddrc_v2 --offset wdq
		else
			ddrc_v2 --offset wdq  2>&1 | tee -a ${1}
		fi
	done
}
O=`getopt -l bb: -- n:f: "$@"` || exit 1

set_file(){
	FILE="$1"
	if [  -e "${FILE}" ]; then
		# echo "FILE was exist!!" 
		# FILE=""
		rm $FILE
		touch $FILE
	else
		touch $FILE
	fi
}
  
eval set -- "$O"

while true; do
        case "$1" in
        -n) COUNT=$2; shift 2;;
        -f) set_file "${2}"; shift 2;;
        --)     shift; break;;
        *)      echo Error; exit 1;;
        esac
done
modprobe ambdram_statis


[ -n "$1" ] && MODE=$1 || exit 1

if echo "$MODE" | grep -q r; then
	get_read "${FILE}"
fi
if echo "$MODE" | grep -q w; then
	get_write "${FILE}"
fi
