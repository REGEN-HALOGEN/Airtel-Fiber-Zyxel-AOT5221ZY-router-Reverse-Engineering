#!/bin/sh
if [ ! -d /var/devinfo ]; then
	    mkdir /var/devinfo
fi

/sbin/mrd_access > /var/devinfo/devinfo.txt

cd /var/devinfo

awk -F= '{
	printf $2 > $1
	for(i=3;i<=NF;i++){
		printf "=" >> $1
		printf $i >> $1
	}
}' devinfo.txt
