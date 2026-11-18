#!/bin/sh
TPL_DET_PIN=504
TPH_DET_PIN=505
BT_DET_PIN=506
ACDC_DET_PIN=46
POE_DET_PIN=47
IR_SKU_PIN=508
IR_PWR_DET_PIN=507
MAIN_SKU_PIN=119
CB_SKU1_PIN=509
CB_SKU2_PIN=510


get_gpioval(){
	[ -n "$1" ]  && PIN_NUM=$1 || exit
	printf %d `amba_debug -g ${PIN_NUM} | grep data | cut -d " " -f 2`
}

BT_TRUTH_TABLE (){
	VAL=`python -c "print($1 << 1 | $2  )"`
	VAL=$((VAL + 1)) # index start from 1
	set -- "TYPE 4, Class: 7, MAX: 60W+" "TYPE 3-4, Class: 5, MAX: 45w" "TYPE 3-4, Class: 4, MAX: 25.5w" "TYPE 3-4, Class: 3, MAX: 12.95w"
	# i=1
	eval echo \$$VAL
	
	# while [ "$#" -gt 0 ]; do
		# echo "{$i, \"$1\"},"
		# i=$((i + 1))
		# shift
	# done
	# (High Loading + HEATER + 4 IR )
	# echo 123
	if [ $VAL -eq 1 -o $VAL -eq 2 ]; then  
		return 0
	else
		return 1 
	fi
}

show_poe_type(){
	ret=1
	echo "TPH=${TPH_VAL}, TPL=${TPL_VAL}, BT=${BT_VAL}"
	
	# Special case
	if [ $BT_VAL -eq 1 -a $TPH_VAL -eq 0 -a $TPL_VAL -eq 0 ]; then
		echo "non-standard POE++ PSE controller but agreed to deliver power request. (60w+)"
		echo "Recommend changing PSE, if you want to do any stress test for Larnaca2"
		return
	fi

	if [ $BT_VAL -eq 0 ]; then 
		echo "PSE: 802.3bt"
		BT_TRUTH_TABLE $TPH_VAL $TPL_VAL
		ret=$?
	else
		echo "PSE: 802.3at/af"
		[ $TPL_VAL -eq 0 ] &&  echo "PSE type: 2(at), Class: 4, Max Power: 25.5w" || echo "PSE type: 1-2(af), Class: 0-4, Max Power: 12.95w"
	fi
	[ $ret -eq 0 ] && echo "Larnaca2 Certifiacated power source." || echo "Recommend changing PSE, if you want to do any stress test for Larnaca2"
	# BT_TRUTH_TABLE $TPH_VAL $TPL_VAL
}

ACDC_DET=`get_gpioval ${ACDC_DET_PIN}`
POE_DET=`get_gpioval ${POE_DET_PIN}`
BT_VAL=`get_gpioval ${BT_DET_PIN}`
TPH_VAL=`get_gpioval ${TPH_DET_PIN}`
TPL_VAL=`get_gpioval ${TPL_DET_PIN}`

IR_SKU_VAL=`get_gpioval ${IR_SKU_PIN}`
IR_PWRDET_VAL=`get_gpioval ${IR_PWR_DET_PIN}`
MAIN_SKU_VAL=`get_gpioval ${MAIN_SKU_PIN}` # 0:TAA ,1:non-TAA
# echo "${IR_PWRDET_VAL}"

echo "HW: `/usr/local/bin/cec_get_sensor_id.sh`"
echo -n "FW ver: `cat /etc/fw_version`"
BUBBLE_SHIELD=-1
if [ ${IR_SKU_VAL} -eq 0 ]; then
	echo -n "(IR),"  
	[ ${IR_PWRDET_VAL} -eq 1 ] && BUBBLE_SHIELD=1 || BUBBLE_SHIELD=0
else
	 echo -n "(non-IR),"
fi
[ $MAIN_SKU_VAL -eq 0 ] && echo " TAA" || echo " non-TAA"

# Bubble shield detect
if [ $BUBBLE_SHIELD -eq 1 ]; then
	echo "Assuming the bubble shield is already covered"
elif [ ${BUBBLE_SHIELD} -eq 0 ]; then
	echo "Assuming the bubble shield is not covered"
else
	echo "Bubble Shiled stat Unknown"
fi

if [ ${ACDC_DET} -eq 1 ]; then
	echo "Power by AC/DC"
elif [ ${POE_DET} -eq 1 ]; then
	show_poe_type
else 
	echo "Unknown power source"
fi  

# poe injector phihong HRV 802.3bt
# amba_debug -g 504
# id 0x000001f8
# data 0x00000001
# amba_debug -g 505
# id 0x000001f9
# data 0x00000000
# amba_debug -g 506
# id 0x000001fa
# data 0x00000000

# poe injector (30w )
# amba_debug -g 504
# id 0x000001f8
# data 0x00000000
# amba_debug -g 505
# id 0x000001f9
# data 0x00000001
# amba_debug -g 506
# id 0x000001fa
# data 0x00000001

# altronix
 # amba_debug -g 504
# id 0x000001f8
# data 0x00000001
# amba_debug -g 505
# id 0x000001f9
# data 0x00000000
# amba_debug -g 506
# id 0x000001fa
# data 0x00000000