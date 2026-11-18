#!/bin/sh
echo "Deply busybox httpd"
cp -af www_cec /www
cp cec_streaming.sh /usr/local/bin/

#Redis Server
mkdir -p /etc/redis
mkdir -p /var/lib/redis

# cp loaddefault /usr/local/bin
# cp default.conf /etc
# cp monitor_writeEnv.sh /usr/local/bin
# cp inotifywait.service /usr/lib/systemd/system/
# ln -sf /usr/lib/systemd/system/inotifywait.service /etc/systemd/system/multi-user.target.wants/inotifywait.service
# cp libinotifytools.so libinotifytools.so.0 libinotifytools.so.0.4.1  /usr/lib

cp redis-server redis-cli /usr/local/bin/
cp redis.conf /etc/redis
cp redis.service /usr/lib/systemd/system/
ln -sf /usr/lib/systemd/system/redis.service /etc/systemd/system/multi-user.target.wants/redis.service


cp httpd.conf /etc
cp httpd.service /usr/lib/systemd/system/
ln -sf /usr/lib/systemd/system/httpd.service /etc/systemd/system/multi-user.target.wants/httpd.service

cp cec_streaming.service /usr/lib/systemd/system/
# ln -sf /usr/lib/systemd/system/cec_streaming.service /etc/systemd/system/multi-user.target.wants/cec_streaming.service

cp shmoo.bmp /etc/shmoo.bmp

# echo 2416 > /etc/project_code
cp filecut  /usr/local/bin


# systemctl start cec_streaming
systemctl start httpd	
# systemctl start redis
loaddefault

start (){
systemctl enable httpd
# systemctl enable redis
systemctl start httpd	
# systemctl start redis
# loaddefault
}

stop(){
systemctl stop httpd	
systemctl stop redis
systemctl disable httpd
systemctl disable redis
}
$1