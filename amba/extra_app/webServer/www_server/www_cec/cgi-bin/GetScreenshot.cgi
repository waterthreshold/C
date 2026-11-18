#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/bin/X11:/usr/local/bin:/usr/local/sbin
IMG="/tmp/screenshot.jpg"
CAMERA_ID="`cat /tmp/Camera`"
if [ "${CAMERA_ID}" == "A" ];then
        SRC_BUFFER_INDEX=0
elif [ "${CAMERA_ID}" == "B" ];then
        SRC_BUFFER_INDEX=4
elif [ "${CAMERA_ID}" == "C" ];then
        SRC_BUFFER_INDEX=6
elif [ "${CAMERA_ID}" == "D" ];then
        SRC_BUFFER_INDEX=8
else 
	echo "Content-Type: image/jpeg"
	echo ""
	echo "error"
	exit 
fi
SENSOR_TYPE=$(cec_get_sensor_id.sh|grep IMX)
if [ "$SENSOR_TYPE" = "IMX675" ];then
        RES_X=2592
        RES_Y=1944
elif [ "$SENSOR_TYPE" = "IMX838" ]; then
        RES_X=3840
        RES_Y=2160
else
        echo "Unknow image sensor!."
        exit
fi
FILE_PREFIX="/tmp/screenshot"
FILE_POSTFIX="_canvas${SRC_BUFFER_INDEX}_"${RES_X}"x"${RES_Y}"_IYUV.yuv"
test_yuvcap -b  ${SRC_BUFFER_INDEX}  -F 0 -Y -f ${FILE_PREFIX}

jpg_enc -v -y ${FILE_PREFIX}${FILE_POSTFIX} -w ${RES_X} -h ${RES_Y} -q 70 -f ${IMG}

echo "Content-Type: image/jpeg"
echo ""

/bin/cat "$IMG"