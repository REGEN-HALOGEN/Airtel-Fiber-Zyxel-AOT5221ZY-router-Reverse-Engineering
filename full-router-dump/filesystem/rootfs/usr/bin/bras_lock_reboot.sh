#!/bin/sh
SLEEP_TIME=$1
REBOOT_PID_FILE=$2

if [ "$SLEEP_TIME" = "" ]; then
        echo "Usage: $0 <sleep time before reboot>"
        exit 1
fi

#reboot
reboot -d $SLEEP_TIME &
echo $! > $REBOOT_PID_FILE
