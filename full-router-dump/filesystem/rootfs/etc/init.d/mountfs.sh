#!/bin/sh

# Refer to USDK PI rc6
/bin/mkdir /tmp/upload
/bin/mkdir /tmp/fwdir

/bin/mkdir -p /var/mnt
/bin/chmod 777 /var/mnt

isPIUBIMTDExist=`grep piubi /proc/mtd`
if [ "$isPIUBIMTDExist" == "" ]
then
	echo "Cannot find piubi partition." > /dev/console
	/bin/mkdir /var/app
	/bin/mount -t ubifs ubi:ubi_apps /var/app
fi
