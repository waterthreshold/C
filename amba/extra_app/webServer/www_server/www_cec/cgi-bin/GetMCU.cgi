#!/bin/sh
source /www/cgi-bin/global.sh
echo -e  "Content-type: text/plain\n"
echo -n "mcu_num=${mcu_num}&"
CMDASCII=65 
for i in `seq 0 $((mcu_num - 1 ))`; do
count=$(( CMDASCII + 2 * i ))
CAMID=`printf "\x$(printf %x $count)"`
ver=`cec_stm32.py --cameraid $CAMID -v  | grep RESP: | cut -d: -f 2`
key="mcu${i}_ver"
eval "val=${ver/~END}"
# echo "CAMID=$CAMID $ver"
echo -n "$key=${val}&"
done