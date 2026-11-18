#!/bin/sh
CONST_DEFAULT_MAC="00:00:00:00:00:00"
get_env_mac(){
	mac=$(upgrade_partition  -e /dev/mmcblk0p6 --show_env | grep mac | cut -d= -f 2 | sed 's/ //')
	echo $mac
}

validation_mac(){
	local_mac=$1
	# echo $local_mac
	[ `echo "$local_mac" | grep -E "^[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}" | wc -c ` -ne 0 ] && return 0 || return 1 
}

set_env_mac(){
	local_mac=$1
	validation_mac ${local_mac}
	if [ $? -eq 0 ]; then
		upgrade_partition  -e /dev/mmcblk0p6 -E -i 0 --mac "$local_mac"
		[ $? -eq 0 ] && echo "Setting $local_mac successfully"  || echo "failed"
	else 
		echo "$local_mac not valid"
	fi
}

# if [ $# -ne 1 ]; then
	# echo "$0 <mac> "
	# echo "  example: $0 12:34:cd:55:55:ab"
	# exit 1 
# fi

if [ -z "$1"  ]; then 
	mac="`ifconfig eth0 | awk -F' ' '/HWaddr/ {print $NF}'`" 
	mac=`echo $mac |  tr  ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz`
	echo "No input mac, detected Original MAC: $mac"
else
	mac=`echo "$1" |  tr  ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz `
fi

set_env_mac $mac 
# validation_mac "12:34:44:55:55:AB"
# validation_mac "12:34:44:55:55:67"
# validation_mac "12:34:cdd:55:55:ab"
# validation_mac "12:34:cd:55:55:ab"
# validation_mac "12:34:44:55:55:AG"