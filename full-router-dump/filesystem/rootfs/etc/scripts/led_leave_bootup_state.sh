#!/bin/bash

## Script to remove "state_bootup" file to recover normal state.

sleep 65

if [ -f /tmp/state_bootup ]; then
	rm -rf /tmp/state_bootup
	echo 0 > /sys/class/leds/LED_WPS_G/brightness
	echo 1 > /sys/class/leds/LED_PWR_G/brightness
fi