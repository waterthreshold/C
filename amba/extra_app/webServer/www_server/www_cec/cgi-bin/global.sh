#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/bin/X11:/usr/local/bin:/usr/local/sbin
mcu_num=2
cam_num=4
sdcard_num=2
usb_num=1

NVRAM_GRP=/etc/nvram/

## function handler
network_hdler_func(){
	if [ `redis-cli get dhcp` = "on" ]; then 
		udhcpc -i eth0 -p /var/run/udhcpc1.pid -s /usr/share/udhcpc/default.script &
	else 
		ifconfig eth0 `redis-cli --raw get ip` netmask `redis-cli --raw get subnet`
	fi 
}
list_camByID()
{
	ASCII_A=65
	for  i in `seq 0 $(( cam_num - 1))`; 
	do
		ASCII=$(( ASCII_A + i ))
		printf "\x`printf "%x " $ASCII`"
		
	done
}


# shmoo_setting()
# {

	# case "$1" in 
		# on)
			# for c in `list_camByID`;
			# do
				# test_loadbmp -${c} -a 0 -x 20 -y 20 -L /etc/shmoo.bmp 
			# done
			# ;;
		
		# off)
			# for c in `list_camByID`;
			# do
				# test_loadbmp -${c} -a 0 --disable
			# done
			# ;;
		# *)
			# echo "unsupport action '$action' found !!"
			# exit 1
	# esac
# }

system_hdler_func(){
	hostnamectl set-hostname `redis-cli get hostname`
	shmoo_setting `redis-cli get shmoo`
}






NETWORK_FLAG=$((1 << 0))
SYSTEM_FLAG=$((1 << 1))
# SHOMOO_FLAG=$((1 << 2))

redis_set_wrap()
{
	key=$1
	value=$2
	grp=$3
	if [ "`redis-cli GET $key`" !=  "$value" ]; then
		redis-cli SET $key $value
		if [ -n "$grp" ]; then
			if type "${grp}_hdler_func" >/dev/null 2>&1; then
				eval "${grp}_hdler_func"
			else
				echo "function Not found"
			fi
		fi
	fi 
}

write_env()
{
	value=`cat /etc/writeEnv`
	if [ $value -ne 0 ]; then
		[ $(( value & NETWORK_FLAG)) -ne 0 ] && network_hdler_func
		[ $(( value & SYSTEM_FLAG)) -ne 0 ] && system_hdler_func
		# [ $(( value & SHOMOO_FLAG)) -ne 0 ] && shmoo_hdler_func 
		echo 0 > /etc/writeEnv
	fi  
}

