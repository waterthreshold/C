#!/bin/sh
BUS=${1-"2"}
eeprom_tool -I > /dev/null
[ $? -ne 0 ]  && echo "Invalid meta data"  && exit 1
directoyname="Bosch_`eeprom_tool  -b $BUS -I | grep "SerialNumber" | cut -d'"' -f2`"
mkdir -p   ${directoyname}/meta
mkdir -p   ${directoyname}/mcu
DESCRIPTION="`eeprom_tool -b $BUS -I | grep "MaterialDescription" | cut -d'"' -f2)`"
LABELMAC="`eeprom_tool -I | grep "LabelMac" | cut -d'"' -f2)`"
SN="`eeprom_tool  -b $BUS -I | grep "SerialNumber" | cut -d'"' -f2)`"
eeprom_tool  -b $BUS -o "${directoyname}/meta/${DESCRIPTION}-${LABELMAC}.bin"
eeprom_tool  -b $BUS -I -o "${directoyname}/meta/eeprom_${SN}.json"

# mcu
CONSOLE_VAL=$(tr ' ' '\n' < /proc/cmdline | grep '^console=' | cut -d'=' -f2)
MAX_RANGE=`basename -a /dev/ttyS*  | grep -v ${CONSOLE_VAL} | wc -l  `
count=1
for tty in 	`basename -a /dev/ttyS*  | grep -v ${CONSOLE_VAL}`
do
	tty="`basename -a /dev/ttyS*  | grep -v ${CONSOLE_VAL} | sed -n "${count}p"`"
	echo $tty
	stm32mcu_tool.sh -f  "${directoyname}/mcu/${LABELMAC}-stm32-${tty}.bin"  ${count}
	count=$(( count + 1  ))
done
