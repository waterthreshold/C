#!/bin/sh

# source global.sh

ntp_server=$(redis-cli --raw get ntp_server)
ntp_enable=$(redis-cli --raw get ntp_enable)
timezone=$(redis-cli --raw get timezone)
time_now=$(/bin/date +"%s")

echo -e  "Content-type: text/plain\n"
echo -n "ntp_server=${ntp_server}&ntp_enable=${ntp_enable}&timezone=${timezone}&time_now=${time_now}"