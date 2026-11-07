#!/bin/sh

INTERFACE_CONFIG_FILE=/sbin/ifconfig
CCC_FILE=/etc/init.d/ccc.sh
CLEAR=/bin/clear
PRINT_NULL="/dev/null 2>&1"
PREFIX=/etc/init.d/

echo "Killing all process & down interface"
NETWORKNAME=`$INTERFACE_CONFIG_FILE | awk '/^[eth|lo|br]/{print $1}'`
INITS="crontab.sh thttpd.sh ftpd.sh telnetd.sh dropbear.sh tftpd.sh qtn.sh ccc.sh dnsmasq.sh zebra.sh zyims.sh tr069.sh syslog-ng.sh zytd.sh"
#INITS="crontab.sh thttpd.sh ftpd.sh telnetd.sh dropbear.sh tftpd.sh dnsmasq.sh zebra.sh tr069.sh syslog-ng.sh zytd.sh"
#INITS="crontab.sh telnetd.sh dropbear.sh  ccc.sh dnsmasq.sh zebra.sh zyims.sh tr069.sh syslog-ng.sh zytd.sh"
/usr/bin/killall -9 check_onuapp_alive.sh
/usr/bin/killall -9 onuapp
/usr/bin/killall -9 bewlan
/usr/bin/killall -9 zy_monitor_wps
/usr/bin/killall -9 zy_wps_button
/usr/bin/killall -9 wscd
/usr/bin/killall -9 ripd
/usr/bin/killall -9 gproxy
/usr/bin/killall -9 klogd
/usr/bin/killall -9 syslog-ng
/usr/bin/killall -9 dropbear
/usr/bin/killall -9 crond
/usr/bin/killall -9 icf.exe
/usr/bin/killall -9 mm.exe
/usr/bin/killall -9 voiceApp
/usr/bin/killall -9 rtdot1xd
/usr/bin/killall -9 ntpclient
/usr/bin/killall -9 smbd
/usr/bin/killall -9 nmbd
/usr/bin/killall -9 rmt_qcsmngr

# 1. stop runnung daemon
echo "Stopping process"
for i in $INITS
do
	#echo "$PREFIX$i stop"
	$PREFIX$i stop
done

# 2. close all network interfaces
useNFS=`mount | grep nfs`
if [ "$useNFS" == ""  ];then
	for nifname in $NETWORKNAME
	do
		echo "$INTERFACE_CONFIG_FILE $nifname down"
		#$INTERFACE_CONFIG_FILE $nifname down
	done
fi

# 3. Clear cache
echo '1' > /proc/sys/vm/drop_caches
