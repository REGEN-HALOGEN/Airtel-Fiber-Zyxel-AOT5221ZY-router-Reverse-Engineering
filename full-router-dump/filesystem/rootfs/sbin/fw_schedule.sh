#!/bin/sh
FW_UPGRADE_SCRIPT=/sbin/fwupgrade.sh
FW_QUEUE_DIR=/var/spool/fw/

if [ -d $FW_QUEUE_DIR ]; then
	for file in `ls $FW_QUEUE_DIR`
	do
		if [ -f $FW_QUEUE_DIR/$file ]; then
			$FW_UPGRADE_SCRIPT
			exit $?
		fi
	done
fi

