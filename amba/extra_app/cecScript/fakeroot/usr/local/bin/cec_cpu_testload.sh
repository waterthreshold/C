#!/bin/sh
killrelateall ()
{
	killall cpulimit
	killall cpu_full_load
	killall top
}
valid_percentage()
{
	if [ `echo $1 | grep -E '^[0-9]{1,3}$' | wc -c` -eq 0  ]; then 
		echo "$1 is not a valid number"
		exit 2	
	fi
	if [  $1 -lt 0 -o $1 -gt 100 ]; then 
		echo "$1% out of range"
		exit 1
	fi
}

printusage(){
cat << EOF

$PROGNAME:

	Usage: $PROGNAME  [number of Percentage] [OPTIONS] 
	Essential 
		<number of Percentage>    0 - 100%	
		
		---
		
        -m              after  setting cpu loading open program top to monitor cpu usage
        -h              print usage
		
	Example:
		$PROGNAME 50[%] -m
EOF
		
}
MONITOR_MODE=0
PROGNAME=${0##*/}
PERCENTAGE=${1//%/}
valid_percentage $PERCENTAGE
shift 1 
# echo $@
O=`getopt -l -- mh "$@"` || exit 1
eval set -- "$O"
while true; do
        case "$1" in
        -m)     MONITOR_MODE=1; shift;;
		-h) 	printusage;exit 0;shift;;
		 --)     shift; break;;
        *)      echo "UNKNOWn $1"; exit 1;;
        esac
done

killrelateall
if [ `ps -o pid,comm | grep cpu_full_load | wc -c` -eq 0 ]; then
	cpu_full_load > /dev/zero &
fi

if [ `ps -o pid,comm | grep cpu_full_load | wc -c` -eq 0 ]; then
	echo "cpu_full_load cannot run properly"
	exit 1 
fi

cpulimit -e cpu_full_load -l $(( PERCENTAGE * 2 )) > /dev/zero &


if [ $MONITOR_MODE -eq 1 ]; 
then
	trap killrelateall SIGINT
	top -d 1 & 
	sleep 300  
	wait 
	
fi
