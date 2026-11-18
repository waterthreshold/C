#!/bin/sh

[ -e "/tmp/Camera" ] && CAMERA_ID=`/bin/cat /tmp/Camera` || RESULT=1
RESULT=0
echo -e  "Content-type: text/plain\n"
echo -n "Camera=${CAMERA_ID}&Code=${RESULT}"