#!/bin/sh

UPLOAD_FILE="/tmp/upload.bin"

echo "Content-Type: text/plain"
echo ""

# CONTENT_LENGTH is provided by CGI
LEN="${CONTENT_LENGTH}"

if [ -z "$LEN" ]; then
    echo "No CONTENT_LENGTH"
    exit 1
fi

# Read POST body from stdin
/bin/dd bs=1 count="$LEN" 2>/dev/null > "$UPLOAD_FILE"

[ $? -ne 0 ] && echo $? && exit
echo 0 > /sys/block/mmcblk0boot0/force_ro
dd if=/dev/zero of=/dev/mmcblk0boot0
sleep 0.3
upgrade_partition -q  -p /dev/mmcblk0boot0 "$UPLOAD_FILE" > /dev/zero
# upgrade_partition  -q -b 1 -p /dev/mmcblk0boot0  "$UPLOAD_FILE" > /dev/zero
if [ $? -eq 0 ];then 
	echo "Upload OK"
else
	echo "Upload Failed"
fi

# sleep 1 
systemctl reboot