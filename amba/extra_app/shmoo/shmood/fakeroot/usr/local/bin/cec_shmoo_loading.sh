#!/bin/sh
get_cavalry_status(){
ca_en=`cavalry_load --status | cut -d: -f 2`
if [ "${ca_en// /}" = "Stopped" ]; then 
	return  0 
elif [ "${ca_en// /}" = "Started" ]; then 
	return 1
else 
	return 2
fi
}
stop_prgm(){
killrelatecpuall
killrelatedmemall
killallvprun
killrelatedstreamall
echo "Terminate all related full loading program !!"
return 0
}
killrelatecpuall ()
{
	killall cpulimit
	# killall memtester-arm
	
	killall cpu_full_load
	# killall top
}

killrelatedmemall(){
	killall memtester-arm
	killall test_memcpy 
}

killallvprun(){
get_cavalry_status
[ $? -ne 0 ] &&  cavalry_load --stop-vp || echo "VP Was Not running!"
}

killrelatedstreamall(){
	killall -9 rtsp_server
	test_encode -A -s
	sleep 0.5
	test_encode -B -s
	sleep 0.5
	test_encode -C -s
	sleep 0.5
	test_encode -D -s
	sleep 0.5
	test_encode --idle --nopreview #-i poweroff
	sleep 0.5
	# rmmod imx838_mipi imx675_mipi
	sleep 0.5
	killall -9 test_aaa_service
	# sleep 0.5
}
valid_percentage()
{
	if [ `echo $1 | grep -E '^[0-9]{1,3}$' | wc -c` -eq 0  ]; then 
		echo "$1 is not a valid number"
		exit 3	
	fi
	if [  $1 -lt 0 -o $1 -gt 100 ]; then 
		echo "$1% out of range"
		exit 4
	fi
}

debug_print(){
	echo "ENABLE_CONFIGUREFILE=${ENABLE_CONFIGUREFILE}"
	echo "CONFIGURE_FILE=${CONFIGURE_FILE}"
	echo "CPU_LOADING_ENABLE=${CPU_LOADING_ENABLE}"
	echo "MEM_LOADING_ENABLE=${MEM_LOADING_ENABLE}"
	echo "VP_LOADING_ENABLE=${VP_LOADING_ENABLE}"
	echo "DSP_LOADING=${DSP_LOADING}"
	# echo "-------------------------------------"
	echo "CPU_PERCENTAGE=${CPU_PERCENTAGE}"
	echo "VP PERCENTAGE=${VP_PERCENTEAGE}"
	echo "MEMTESTER_TESTSIZE=${MEMTESTER_TESTSIZE}"
	echo "MEMTESTER_INSTANCE=${MEMTESTER_INSTANCE}"
}



printusage(){
cat << EOF

$PROGNAME:
	This program helping setting SHMOO loadding
	Usage: $PROGNAME [OPTIONS] 
	Rule: 
		<number of Percentage>    0 - 100%	
	
	OPTIONS:
		---
		
		-s				Stop all related loading ex. CPU, Memory, VP 
		-C				Enable CPU loading
		-M				Enable memtester loading
		-D 				Enable Streaming	(default: disable)
		-V				Enable Vector processor loading
		--CP			Setting CPU loadding percetage (default. ${CPU_PERCENTAGE}%)
		--VP			Setting vector processor loading percentage  (default. ${VP_PERCENTEAGE}%)
		--MS			Setting memtester Size  (default. ${MEMTESTER_TESTSIZE})
		--MC			run memtester process (default. ${MEMTESTER_INSTANCE})
		-h				print usage
		
	Example:
		$PROGNAME -CMV
		$PROGNAME -s
		$PROGNAME -CMV --MC 1
EOF
exit 2
}

CPU_LOADING_ENABLE=0
MEM_LOADING_ENABLE=0
VP_LOADING_ENABLE=0
DSP_LOADING=0
CPU_PERCENTAGE=100
VP_PERCENTEAGE=100
MEMTESTER_TESTSIZE="1G"
MEMTESTER_INSTANCE=4
PROGNAME=${0##*/}
PERCENTAGE=${1//%/}
SET_DEBUG_PRINT=0
CONFIGURE_FILE="/etc/shmoo.json"
ENABLE_CONFIGUREFILE=0
valid_percentage $VP_PERCENTEAGE
# shift 1 
# echo $@
O=`getopt -l CP: -l VP: -l MS: -l MC: -- CSMDVsdhc: "$@"` || exit 1
eval set -- "$O"
while true; do
        case "$1" in
        -C)     CPU_LOADING_ENABLE=1; shift;;
		-M) 	MEM_LOADING_ENABLE=1; shift;;
		-V) 	VP_LOADING_ENABLE=1; shift;;
		-D) 	DSP_LOADING=1; shift;;
		-s) 	stop_prgm; shift;;
		-c)		ENABLE_CONFIGUREFILE=1;CONFIGURE_FILE="$2"; shift 2;;
		-d)    SET_DEBUG_PRINT=1; shift;;
		 --CP) CPU_PERCENTAGE=$2;valid_percentage ${CPU_PERCENTAGE}; shift 2;; 
		 --VP) VP_PERCENTEAGE=$2;valid_percentage ${VP_PERCENTEAGE}; shift 2;;
		 --MS) MEMTESTER_TESTSIZE=$2 shift 2;;
		 --MC) MEMTESTER_INSTANCE=$2;valid_percentage ${CPU_PERCENTAGE}; shift 2;;
		 --)  shift; break;;
		 
		-h) printusage;;
        *)      echo "UNKNOWn $1"; printusage;exit 1;;
        esac
done

# killrelateall
run_cpu_loading (){
PERCENTAGE=${1}
if [ `ps -o pid,comm | grep cpu_full_load | wc -c` -eq 0 ]; then
	cpu_full_load > /dev/zero &
fi

# if [ `ps -o pid,comm | grep cpu_full_load | wc -c` -eq 0 ]; then
	cpulimit -e cpu_full_load -l $(( PERCENTAGE * 2 )) > /dev/zero &
# fi

}

validation_sizeform(){
	str=`echo ${1} | tr abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ` 
	
	echo $str |  grep -qE "\d*[KMG]$"
	[ $? -ne 0 ] && echo "size form error ex.128M,2G" && exit 4
	UNIT=`echo ${str:0-1}` 
	LENGTH=${#str}
	LENGTH=$(( LENGTH - 1 ))
	result=`echo ${str:0:LENGTH}`
	if [ "$UNIT" = "K" ]; then
		unit_size=$(python -c "print(${result} * (1<<10))")
	elif [ "$UNIT" = "M" ]; then
		unit_size=$(python -c "print(${result} * (1<<20))")
	elif [ "$UNIT" = "G" ]; then
		unit_size=$(python -c "print(${result} * (1<<30))")
	fi
	printf %#x ${unit_size}
}	

run_mem_loading(){
	COUNT=$1
	# SIZE=`validation_sizeform "${2}"`
	SIZE=$2
	for in in `seq 1 ${COUNT}`; 
	do
		memtester-arm ${SIZE} > /dev/zero &
	done 
	# test_memcpy -s ${SIZE} -c 0 -t ${COUNT} -m 1 &
}

run_vp_loading(){
if [ `lsmod | grep cavalry | wc -l` -eq 0 ]; then
	modprobe cavalry;
fi
get_cavalry_status
if [ $? -eq 0 ]; then
cavalry_load -f /lib/firmware/cavalry.bin
test_nnctrl -b /root/onnx_yolov3_cavalry-cv5.bin --in input.1 -e -t 0 > /dev/zero &
fi
}

parser_config(){
	if [ ! -e "$CONFIGURE_FILE" ];  then 
		CONFIGURE_FILE="/etc/shmoo.json"
		[ ! -e "$CONFIGURE_FILE" ] && echo "Not exist configure file /etc/shmoo.json" && exit 2
	fi
	if jq -e '.loading | has("CPU")' "$CONFIGURE_FILE" > /dev/null; then
		CPU_LOADING_ENABLE=1
		CPU_PERCENTAGE=`jq -r '.loading.CPU.Percentage' "$CONFIGURE_FILE"`
	else 
		CPU_LOADING_ENABLE=0
	fi
	if jq -e '.loading | has("MEM")' "$CONFIGURE_FILE" > /dev/null; then
		MEM_LOADING_ENABLE=1
		MEMTESTER_TESTSIZE=`jq -r '.loading.MEM.SIZE' "$CONFIGURE_FILE"`
		MEMTESTER_INSTANCE=`jq -r '.loading.MEM.COUNT' "$CONFIGURE_FILE"`
	else 
		CPU_LOADING_ENABLE=0
	fi
	
	if jq -e '.loading | has("VP")' "$CONFIGURE_FILE" > /dev/null; then
		VP_LOADING_ENABLE=1
		VP_PERCENTEAGE=`jq -r '.loading.VP.Percentage' "$CONFIGURE_FILE"`
	else 
		VP_LOADING_ENABLE=0
	fi
	
	
}
run_dsp_loading(){
	[ -e "/usr/local/bin/cec_init.sh" ] && /usr/local/bin/cec_init.sh streaming_init
}
[ $ENABLE_CONFIGUREFILE -eq 1  ] && parser_config 
if [ ${CPU_LOADING_ENABLE} -eq 1  ]; then
run_cpu_loading  ${CPU_PERCENTAGE}
fi

if [ ${MEM_LOADING_ENABLE} -eq 1  ]; then
run_mem_loading ${MEMTESTER_INSTANCE} ${MEMTESTER_TESTSIZE}
fi

if [ ${VP_LOADING_ENABLE} -eq 1  ]; then
run_vp_loading  ${VP_PERCENTEAGE}
fi
[ ${SET_DEBUG_PRINT} -eq 1 ] && debug_print

if [ ${DSP_LOADING} -eq 1 ]; then 
run_dsp_loading
fi
exit 0