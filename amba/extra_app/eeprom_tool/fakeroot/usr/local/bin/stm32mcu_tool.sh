#!/bin/sh

# Exit immediately if a command exits with a non-zero status
# set -e

# Configuration
BINARY="stm32flash lsgpio amba_debug"
WRITE_MODE=0
INPUT_FILE=""

# GPIO_MCU_1_BOOT=55
# GPIO_MCU_2_BOOT=56

# GPIO_MCU_1_RST=51
# GPIO_MCU_2_RST=52


set_gpio()
{
	gpio=$1
	status=$2
	echo "set gpio: ${gpio} ${status} "
	amba_debug -g $gpio -d $status
}

enter_upgrademode(){
	local idex=$(( $1 - 1  ))
	gpio_mcu_boot=$(lsgpio | grep -i "McuBoot${idex}" |  awk '{print $2}' | tr -d ':' )
	gpio_mcu_rst=$(lsgpio | grep -i "McuRst${idex}" |  awk '{print $2}' | tr -d ':' )
	echo "mcu_boot gpio: ${gpio_mcu_boot} mcu reset gpio: ${gpio_mcu_rst}"
	set_gpio ${gpio_mcu_boot} 1
	sleep 1

	#=====Reset MCU
	set_gpio ${gpio_mcu_rst} 0
	sleep 1
	set_gpio  ${gpio_mcu_rst} 1
	sleep 2
}

reset_mcu(){
		local idex=$(( $1 - 1  ))
		gpio_mcu_boot=$(lsgpio | grep -i "McuBoot${idex}" |  awk '{print $2}' | tr -d ':' )
		gpio_mcu_rst=$(lsgpio | grep -i "McuRst${idex}" |  awk '{print $2}' | tr -d ':' )
		echo "mcu_boot gpio: ${gpio_mcu_boot} mcu reset gpio: ${gpio_mcu_rst}"
		set_gpio ${gpio_mcu_boot} 0
        sleep 1	
        #=====Reset MCU
        set_gpio ${gpio_mcu_rst} 0
        sleep 1
        set_gpio ${gpio_mcu_rst} 1
}

# Help / Usage presentation function
print_usage() {
    echo "============================================================"
    echo "  EEPROM Traverse & Utility Tool (Shell Wrapper)"
    echo "============================================================"
    echo "Usage:"
    echo "  $0 [OPTIONS] ttyS[index]"
    echo ""
    echo "Options:"
    echo "  -f <path>  specific file path: write mode: Firmware, Non-Writemode: dump firmware"
    echo "  -w              Enable write/copy mode (requires -i and -o)"
    echo "  -h              Display this help and exit"
    echo ""
    echo "Examples:"
    echo "  dump ttyS<index 1> to file /root/larnaca2-dump2.bin :"
    echo "    $0  -f /root/larnaca2-dump2.bin 1"
    echo ""
    echo "  Flash /root/larnaca2-stm32-dev.bin to via ttyS<index 2>:"
    echo "    $0 -w  -f /root/larnaca2-stm32-dev.bin 2"
    echo ""
    echo "============================================================"
}

# Parse command-line flags using getopts
while getopts "wf:h" opt; do
    case ${opt} in
        w)
            WRITE_MODE=1
            ;;
        f)
            INPUT_FILE="$OPTARG"
            ;;
        h)
            print_usage
            exit 0
            ;;
        \?)
            print_usage
            exit 1
            ;;
    esac
done
shift $((OPTIND - 1))
MCU_ID=$1
if [[ "$MCU_ID" =~ ^[0-9]+$ ]] && [[ $MCU_ID > 0 ]]; then
    echo "Success: MCU_ID ($MCU_ID) is a valid positive number."
else
    echo "Error: MCU_ID must be a positive integer greater than 0." >&2
    exit 1
fi
CONSOLE_VAL=$(tr ' ' '\n' < /proc/cmdline | grep '^console=' | cut -d'=' -f2)
MAX_RANGE=`basename -a /dev/ttyS*  | grep -v ${CONSOLE_VAL} | wc -l `
if ! [ $MAX_RANGE -ge ${MCU_ID} ];  then
	echo "MAXRANGE not greater than MCUID: ${$MCU_ID}"
	exit 1 
fi
TTYS_PATH="`basename -a /dev/ttyS*  | grep -v ${CONSOLE_VAL} | sed -n "${MCU_ID}p"`"
TTYS_PATH="/dev/${TTYS_PATH}"
# if [[ "$TTYS_PATH" =~ "ttyS*" ]]; then
	# TTYS_PATH="/dev/${TTYS_PATH}"
	# echo $TTYS_PATH
# else	
	# echo "Something got wrong!!"
	# exit 1
# fi
# Ensure the compiled C binary exists
for cmd in ${BINARY}; do
	if command -v ${cmd} &>/dev/null; then
		echo "${cmd} is available!"
	else
		echo "Error: ${cmd} is missing." >&2
		exit 1
	fi
done 


# Validate that input file was provided
if [ -z "$INPUT_FILE" ]; then
    echo "Error: Missing required option -i <input_file>" >&2
    echo ""
    print_usage
    exit 1
fi
echo "Input File: ${INPUT_FILE}"
# eval enter_upgrademode "\$GPIO_MCU_${MCU_ID}_BOOT" "\$GPIO_MCU_${MCU_ID}_RST"
enter_upgrademode ${MCU_ID}
# Execute workflow based on mode
if [ "$WRITE_MODE" -eq 1 ]; then
    
   stm32flash  -w  $INPUT_FILE  -v ${TTYS_PATH}
else
    # Info / Parse Mode
    stm32flash -r $INPUT_FILE ${TTYS_PATH}
fi
# eval reset_mcu "\$GPIO_MCU_${MCU_ID}_BOOT" "\$GPIO_MCU_${MCU_ID}_RST"
# reset_mcu `eval echo \$GPIO_MCU_${MCU_ID}_BOOT` `eval echo \$GPIO_MCU_${MCU_ID}_RST`
reset_mcu ${MCU_ID}