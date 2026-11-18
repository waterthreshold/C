#!/bin/sh

#SetNetwork.cgi
#Type=<static/dhcp>
#IpAddress=<IP Format>
#NetMask=<IP format>
# dhcp=on&ip=172.16.7.69&subnet=255.255.255.0&gateway=172.16.7.255&dns=172.16.199.1

# TestCase
#
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/bin/X11:/usr/local/bin:/usr/local/sbin
INTERFACE=eth0
echo "Content-type: text/plain"
echo ""

# read -n "$CONTENT_LENGTH" POST_STRING
# while IFS= read -r cmd; do
	# echo "$cmd"
	# eval "$cmd"
# done < <(ls)
# echo "$QUERY_STRING" | \
# awk '{
    # n = split($0, pairs, "&");
    # for (i = 1; i <= n; i++) {
        # split(pairs[i], kv, "=");
        # print kv[1] "=" kv[2];
    # }
# }' | while IFS= read -r cmd; do
	# echo "eval $cmd"
	# eval "$cmd"
# done 

while IFS= read -r cmd; do
    # echo "eval $cmd"
    eval "$cmd"
done <<EOF
$(echo "$QUERY_STRING" | awk '{
    n = split($0, pairs, "&");
    for (i = 1; i <= n; i++) {
        split(pairs[i], kv, "=");
        print kv[1] "=" kv[2];
    }
}')
EOF

# eval "redis-cli set foo bar"
if [ "$dhcp" = "on" ]; then 
udhcpc -i eth0 -p /var/run/udhcpc1.pid -s /usr/share/udhcpc/default.script
redis-cli SET dhcp on
# echo 000
elif [ "$dhcp" = "off" ]; then 
ifconfig ${INTERFACE} ${ip} netmask ${subnet}
redis-cli  SET dhcp off > /dev/null
redis-cli SET ip ${ip} > /dev/null
redis-cli  SET subnet ${subnet} > /dev/null
# echo 111
redis-cli   SET gateway ${gateway} > /dev/null
redis-cli  SET dns ${dns} > /dev/null
fi 
echo "code=0"