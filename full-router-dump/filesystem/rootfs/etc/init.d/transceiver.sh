#!/bin/sh /etc/rc.common

START=50

start() {
	test -c /dev/pon_transceiver || mknod /dev/pon_transceiver c 339 0

	file="/etc/transceiver_module.sh"
	if [ -f "$file" ]
	then 
	   exec "$file"
	fi
}
