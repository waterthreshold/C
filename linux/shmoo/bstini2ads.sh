#!/bin/bash
if [[ "$(basename "$PWD")" != "ambarella" ]]; then
    echo "No, you are in '$(basename "$PWD")'."
	exit 1
fi
[ ! -e 'boot/amboot/src/bst/tools/bstiniparser' ] && echo "bstiniparser not exist" && exit 1 
board_dir="`cat ../.soc`_`cat ../.board`"

[ ! -d "boards/${board_dir}" ] && echo "${board_dir} not exist" && exit 1
target_dir="boards/${board_dir}/bsp"
mkdir -p boards/${board_dir}/bsp/ads
for ini in `find ${target_dir} -name "*.ini"`
do
	adsname="${ini//\.ini}.ads"
	echo ${adsname##*/}
	boot/amboot/src/bst/tools/bstiniparser --for usb ${ini} > "boards/${board_dir}/bsp/ads/${adsname##*/}"
done

