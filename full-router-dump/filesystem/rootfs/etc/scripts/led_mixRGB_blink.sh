#!/bin/sh

# blue
echo timer > /sys/class/leds/LED_FXS/trigger
echo 500 > /sys/class/leds/LED_FXS/delay_on
echo 500 > /sys/class/leds/LED_FXS/delay_off

#red
echo timer > /sys/class/leds/LED_PWR_G/trigger
echo 500 > /sys/class/leds/LED_PWR_G/delay_on
echo 500 > /sys/class/leds/LED_PWR_G/delay_off

#green
echo timer > /sys/class/leds/LED_USB0/trigger
echo 500 > /sys/class/leds/LED_USB0/delay_on
echo 500 > /sys/class/leds/LED_USB0/delay_off