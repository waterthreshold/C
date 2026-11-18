#!/bin/sh
DEFAULT_CAMERAID=0

load_image_sensor_driver()
{
	init.sh --na

        # sleep 0.2
        # amba_debug -g 67 -d 0
        # sleep 0.1
        # amba_debug -g 68 -d 0
        # sleep 0.1
        # amba_debug -g 67 -d 1
        # sleep 0.1
        # amba_debug -g 68 -d 1
        # sleep 0.1
        # amba_debug -g 116 -d 0
        # amba_debug -g 36 -d 0
        # amba_debug -g 40 -d 0
        # amba_debug -g 41 -d 0
        # sleep 0.2
        # amba_debug -g 41 -d 1
        # sleep 0.1
        # amba_debug -g 40 -d 1
        # sleep 0.1
        # amba_debug -g 36 -d 1
        # sleep 0.1
        # amba_debug -g 116 -d 1
	# sleep 0.5

	# /usr/bin/i2cset -f -y 0 0x36 0x3000 0	#enter image sensor standby mode
	# sleep 0.5
	
	if [ "$(cec_get_sensor_id.sh|grep IMX675)" != "" ];then
		modprobe imx675_mipi vinc_id=0x40b8 addr=0x36363636 lane=4
	elif [ "$(cec_get_sensor_id.sh|grep IMX838)" != "" ];then
		modprobe imx838_mipi vinc_id=0x40b8 addr=0x36363636 lane=4 
	fi

}

streaming_init()
{
	echo "streaming init." > /dev/kmsg
	
	load_image_sensor_driver

	# sleep 1
	test_aaa_service -a &
	# sleep 2

	if [ "$(cec_get_sensor_id.sh|grep IMX675)" != "" ];then
		test_encode --resource-cfg /etc/ext_scripts/cv5_larnaca2_4_vin_2592x1944_linear.lua  --vout-cfg /usr/share/ambarella/lua_scripts/vout_hdmi.lua
		# sleep 1
		# test_encode -A -H 2592x1944 -b 0 -e
		# test_encode -B -H 2592x1944 -b 4 -e
		# test_encode -C -H 2592x1944 -b 6 -e
		# test_encode -D -H 2592x1944 -b 8 -e
		# rtsp_server &
	elif [ "$(cec_get_sensor_id.sh|grep IMX838)" != "" ];then
		test_encode --resource-cfg /etc/ext_scripts/cv5_larnaca2_4_vin_3840x2160_linear.lua  --vout-cfg /usr/share/ambarella/lua_scripts/vout_hdmi.lua
		# sleep 1
		# test_encode -A -H 3840x2160 -b 0 -e
		# test_encode -B -H 3840x2160 -b 4 -e
		# test_encode -C -H 3840x2160 -b 6 -e
		# test_encode -D -H 3840x2160 -b 8 -e
		# rtsp_server &
	fi

	
}

encode() {
    local CAMERA_ID="$1"
    local H=1080
    local W=1920
    local SRC_BUFFER_INDEX

    case "${CAMERA_ID}" in
        A) SRC_BUFFER_INDEX=0 ;;
        B) SRC_BUFFER_INDEX=4 ;;
        C) SRC_BUFFER_INDEX=6 ;;
        D) SRC_BUFFER_INDEX=8 ;;
        *)
            echo "Failed" >&2
            return 1  # Use return instead of exit so it doesn't kill the parent shell
            ;;
    esac

    # Run the test command
    if  test_encode -"${CAMERA_ID}" -H "${W}x${H}" -b "${SRC_BUFFER_INDEX}" -e; then
        echo "A" > /tmp/Camera
        echo "${W}" > /tmp/encode_w
        echo "${H}" > /tmp/encode_h
    fi
}

start(){
streaming_init
# cec_init.sh streaming_init
jpg_http_stream -b ${DEFAULT_CAMERAID} -p 8080 -f 30 >/dev/null &
encode "A"
rtsp_server &
}

# Imvalid initialize in twice
stop(){ 
echo "Terminate the cec_streaming" > /dev/kmsg
	

killall -9 rtsp_server
sleep 0.5
test_encode -A -s
sleep 0.5
test_encode -B -s
sleep 0.5
test_encode -C -s
sleep 0.5
test_encode -D -s
sleep 0.5
test_encode  --stop-multi a~d
sleep 0.5
test_encode -A -b 0 --abort-encode
sleep 0.5
test_encode -B -b 4 --abort-encode
sleep 0.5
test_encode -C -b 6 --abort-encode
sleep 0.5
test_encode -D -b 8 --abort-encode
sleep 0.5
test_encode --idle --nopreview #-i poweroff
sleep 0.5
# rmmod imx838_mipi imx675_mipi
sleep 0.5
killall -9 test_aaa_service
sleep 0.5
rmmod ambarella_fb

}

case "$1" in
	start)
		start
		;;
	stop)
		stop
		;;

	*)
		echo "Failed"
		exit 1
		;;
esac
