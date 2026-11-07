#!/bin/sh
# parse /sys/bus/usb/devices/$2
# output file => /var/usb/$2
# $1 = add or remove
# $2 = port number

#set -x
export PATH="$PATH:/usr/bin:/usr/sbin"

MATCH_DEVICE_INFO="/var/usb/$2"
MATCH_DEVICE_PATH="/sys/bus/usb/devices/$2"

	if [ "$1" = "add" ]; then
		if [ -e $MATCH_DEVICE_PATH ]; then
			MATCH_DEVICE_INFO="/var/usb/$2"
			if [ ! -e $MATCH_DEVICE_INFO ]; then
				echo "[$0] add $MATCH_DEVICE_INFO" > /dev/console
				parameter=`cat $MATCH_DEVICE_PATH/uevent | grep PRODUCT | cut -f 2 -d = `
				echo "usbname:usb_$2" >> $MATCH_DEVICE_INFO
				echo "port:$2" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/devnum`
				echo "devnum:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/version`
				echo "version:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bDeviceClass`
				echo "bDeviceClass:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bDeviceSubClass`
				echo "bDeviceSubClass:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bcdDevice`
				echo "bcdDevice:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bDeviceProtocol`
				echo "bDeviceProtocol:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bNumInterfaces`
				echo "bNumInterfaces:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/idProduct`
				echo "idProduct:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/idVendor`
				echo "idVendor:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/manufacturer`
				echo "manufacturer:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/speed`
				echo "speed:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/maxchild`
				echo "maxchild:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/product`
				echo "product:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/serial`
				echo "serial:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bNumConfigurations`
				echo "bNumConfigurations:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/bNumInterfaces`
				echo "bNumInterfaces:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/$2:1.0/bInterfaceClass`
				echo "bInterfaceClass:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/$2:1.0/bInterfaceNumber`
				echo "bInterfaceNumber:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/$2:1.0/bInterfaceProtocol`
				echo "bInterfaceProtocol:$parameter" >> $MATCH_DEVICE_INFO
				parameter=`cat $MATCH_DEVICE_PATH/$2:1.0/bInterfaceSubClass`
				echo "bInterfaceSubClass:$parameter" >> $MATCH_DEVICE_INFO
			fi
		fi
	elif [ "$1" = "remove" ]; then
		MATCH_DEVICE_INFO="/var/usb/$2"
		if [ -e "$MATCH_DEVICE_INFO" -a "$MATCH_DEVICE_INFO" != "/var/usb/" ]; then
			echo "[$0] remove $MATCH_DEVICE_INFO" > /dev/console
			rm $MATCH_DEVICE_INFO
		fi
	fi
