#!/bin/sh
SLEEP_TIME=$1

if [ "$SLEEP_TIME" = "" ]; then
        echo "Usage: $0 <sleep time before reboot>"
        exit 1
fi

#log & sleep
echo sleep $SLEEP_TIME sec before reboot  > /dev/console
sleep $SLEEP_TIME

#ppp disconnect
echo kill pppd > /dev/console
killall pppd

#reboot
reboot