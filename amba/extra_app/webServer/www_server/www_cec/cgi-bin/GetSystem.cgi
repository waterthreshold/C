#!/bin/sh

source ./global.sh
echo -e  "Content-type: text/plain\n"

hostname=`/bin/hostname -s`
# hwver=`cec_get_hw_version.sh  mb`
fwver="`/bin/cat /etc/fw_version`"

sensorType=`cec_get_sensor_id.sh`
SDK="$(hostnamectl  | /bin/grep 'Operating System' | /bin/sed  -n  's/.*(\(.*\))$/\1/p')"
uptime=$(/bin/cat /proc/uptime)
shmoo=$(redis-cli --raw get shmoo)
# timestamp=$(redis-cli --raw get timestamp)

# uptime=${uptime%%\.*}
echo -n "hostname=${hostname}&fwver=${fwver}&sensorType=${sensorType}&SDK=${SDK}&uptime=${uptime%%\.*}&shmoo=${shmoo}&timestamp=${timestamp}"
# ACSII A = 65
