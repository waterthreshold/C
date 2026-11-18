#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/bin/X11:/usr/local/bin:/usr/local/sbin

echo "Content-type: text/plain"
echo ""

# . /www/cgi-bin/util.sh

dhcp="$(redis-cli --raw GET dhcp)"
# echo $Proto
if [ "$dhcp" = "on" ]; then
	IP_ADDRESS=$(ifconfig eth0 | grep inet | sed 's/^[[:space:]]*inet //' | awk '{print $1}' | cut -d: -f 2)
	NETMASK=$(ifconfig eth0 | grep inet | sed 's/^[[:space:]]*inet //' | awk '{print $3}' | cut -d: -f 2)
	GATEWAY=$(ifconfig eth0 | grep inet | sed 's/^[[:space:]]*inet //' | awk '{print $2}' | cut -d: -f 2)
	DNS1=`cat /etc/resolv.conf  | grep nameserver | head -n 1 | awk '{print $2}'`
	DNS2=`cat /etc/resolv.conf  | grep nameserver | sed -n '2p' | awk '{print $2}'`
	echo "dhcp=on&ip=${IP_ADDRESS}&subnet=${NETMASK}&gateway=${GATEWAY}&dns=${DNS1}&DNS2=${DNS2}"
elif [ "$dhcp" = "off" ]; then
	IP_ADDRESS=$(redis-cli --raw GET ip)
	NETMASK=$(redis-cli --raw GET subnet)
	GATEWAY=$(redis-cli --raw GET gateway)
	DNS1=$(redis-cli --raw GET dns)
	# DNS2=$(redis-cli --raw GET dns)
	
	echo "dhcp=off&ip=${IP_ADDRESS}&subnet=${NETMASK}&gateway=${GATEWAY}&dns=${DNS1}&DNS2=${DNS2}"
	
else
	echo "code=1"
fi 