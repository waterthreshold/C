#!/bin/sh

# source ./gobal.sh
echo -e  "Content-type: text/plain\n"
/bin/df -h -t vfat | awk -f ./storage.awk