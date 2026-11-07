#!/bin/sh
#echo "post save!!!"
#/usr/bin/lzma -c $1 -n $1.lz
#echo "1st parameter is pdm: $1, 2nd is rdm latest: $2"
touch /tmp/ccc_postsave_inprogress
/usr/bin/lzma -c $1 -n $1.lz

#if [ $# -ne 2 ];then
	stat -c --print=%y $1 | cut -c -27 | cut -c 9- | awk -F"-" '{print $1$2$3}' | awk -F" " '{print $1$2}' | awk -F":" '{print $1$2"."$3}' > /var/tmp/timestamp
	mcputil modify 60 $1.lz 61 /var/tmp/timestamp
	rm -f $1.lz
	rm -f /var/tmp/timestamp
	rm -f /tmp/ccc_postsave_inprogress
	
	exit 0
#elif [ ! -e $2 ];then
#	stat -c --print=%y $1 | cut -c -27 | cut -c 9- | awk -F"-" '{print $1$2$3}' | awk -F" " '{print $1$2}' | awk -F":" '{print $1$2"."$3}' > /var/tmp/timestamp
#	mcputil modify 60 $1.lz 61 /var/tmp/timestamp
#	rm -f $1.lz
#	rm -f /var/tmp/timestamp
#	mcputil del 62 63
#	exit 0
#else
#	stat -c --print=%y $1 | cut -c -27 | cut -c 9- | awk -F"-" '{print $1$2$3}' | awk -F" " '{print $1$2}' | awk -F":" '{print $1$2"."$3}' > /var/tmp/timestamp1
#	stat -c --print=%y $2 | cut -c -27 | cut -c 9- | awk -F"-" '{print $1$2$3}' | awk -F" " '{print $1$2}' | awk -F":" '{print $1$2"."$3}' > /var/tmp/timestamp2
#	mcputil modify 60 $1.lz 61 /var/tmp/timestamp1 62 $2 63 /var/tmp/timestamp2
#	rm -f /var/tmp/timestamp1 /var/tmp/timestamp2
#fi
