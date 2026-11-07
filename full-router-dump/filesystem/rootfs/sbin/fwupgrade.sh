#!/bin/sh
FW_UTIL=/sbin/fw_utils.sh
FW_KILL_PROCESS=/sbin/kill_all_process.sh
PRINT_NULL=/dev/null
# store original state

# set state and LED

######## 0. Print firmware upgrade information
clear
echo "Starting firmware upgrade"

######## 1. Check product model & checksum

##### ingore check now ################
$FW_UTIL check
result=$?
if [ "$result" != "0" ]; then
        exit $result
fi


######## 2. Kill all running processes
$FW_KILL_PROCESS


######## 3. unpact ras.bin and generate file list
$FW_UTIL extract
result=$?
if [ "$result" != "0" ]; then
	 exit $result
fi


######## 4. Choose which image we will upgrade to
#USED_IMAGE=`/sbin/fw_printenv -n bootImage`
#if [ "$1" == "0" ] || [ "$1" == "1" ]; then
#	NEW_IMAGE=$1
#else
#	if [ "$USED_IMAGE" == "1" ]; then
#		NEW_IMAGE=0
#	else
#		NEW_IMAGE=1	
#	fi
#fi


######## 5. Program flash
#$FW_UTIL write_flash $NEW_IMAGE
$FW_UTIL write_flash
result=$?
if [ "$result" != "0" ]; then
        exit $result
fi


######## 6. Update ENV
#$FW_UTIL update_ENV $NEW_IMAGE
$FW_UTIL update_TLV
result=$?

# Log firmware upgrade action
# set LED back first


######## 7. System Reset
$FW_UTIL reboot

exit 0
