#!/bin/sh
source /www/cgi-bin/global.sh
echo -e  "Content-type: text/plain\n"
echo -n "cam_num=${cam_num}&"
for i in `seq 0 $(( cam_num - 1))`; 
do
	x=`cat /proc/bosch_imu${i}/in_accel_x_raw`
	y=`cat /proc/bosch_imu${i}/in_accel_y_raw`
	z=`cat /proc/bosch_imu${i}/in_accel_z_raw`
	echo -n "cam${i}_pos=${x},${y},${z}&"
done