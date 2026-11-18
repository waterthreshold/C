#!/bin/sh




echo -e  "Content-type: text/html\n\n"
[ `/bin/ps -o comm | /bin/grep "jpg_http_stream" | /usr/bin/wc -c` -ne 0 ] &&  killall jpg_http_stream   #jpg_http_stream
# ps
# ps -o comm | grep "jpg_http_stream"
RESULT=$?
path="$QUERY_STRING"
ORIGINAL_CAMERA="`cat /tmp/Camera`"
while IFS= read -r line; do
    key=`echo $line | cut -d'=' -f 1`
	val=`echo $line | cut -d'=' -f 2`
	#echo "$line key:$key val:$val"
	if [ "$key" = "Camera" ];then
		CAMERA_ID=$val
	fi 	
done <<EOF
$path 
EOF

if [ "${CAMERA_ID}" == "A" ];then
        SRC_BUFFER_INDEX=0
elif [ "${CAMERA_ID}" == "B" ];then
        SRC_BUFFER_INDEX=4
elif [ "${CAMERA_ID}" == "C" ];then 	
        SRC_BUFFER_INDEX=6
elif [ "${CAMERA_ID}" == "D" ];then
        SRC_BUFFER_INDEX=8
else
      echo "<html><body>Failed</body></html>"
		exit 1
fi
test_encode -${ORIGINAL_CAMERA} -s
/bin/sleep 1.5
test_encode -"${CAMERA_ID}" -H "${W}x${H}" -b "${SRC_BUFFER_INDEX}"
jpg_http_stream -b ${SRC_BUFFER_INDEX} -p 8080 -f 30 >/dev/null &
echo $CAMERA_ID > /tmp/Camera
#echo $PATH
echo "<html><body>CAMERA_ID=${SRC_BUFFER_INDEX}&code=${RESULT}</body></html>"

