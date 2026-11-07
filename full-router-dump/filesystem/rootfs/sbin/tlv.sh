#!/bin/sh
if [ ! -d /var/fwinfo ]; then
	    mkdir /var/fwinfo
fi

/sbin/TLV_access > /var/fwinfo/fwinfo.txt

cd /var/fwinfo

awk -F= '{
	printf $2 > $1
	for(i=3;i<=NF;i++){
		printf "=" >> $1
		printf $i >> $1
	}
}' fwinfo.txt
