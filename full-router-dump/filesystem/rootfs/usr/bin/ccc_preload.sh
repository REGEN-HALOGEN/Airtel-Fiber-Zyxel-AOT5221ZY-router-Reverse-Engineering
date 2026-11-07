#!/bin/sh
# Incoude MLD confiuratoin file
if [ -e /etc/MLD_Config.sh ]; then
    . /etc/MLD_Config.sh
fi

#echo "preload!!!"
#echo "1st parameter is $1, 2nd is $2"
#check and read config.xml, config.rdm.latest

#if [ $# -eq 2 ];then
#	if [ ! -s $1 -a ! -s $2 ];then
#		mcputil read 60 $1.lz 61 /var/tmp/timestamp1 62 $2 63 /var/tmp/timestamp2
#		/usr/bin/lzma -d $1.lz -n $1
#		rm -f $1.lz
#		if [ -e /var/tmp/timestamp1 ];then
#			cat /var/tmp/timestamp1 | xargs touch $1 -t
#			rm -f /var/tmp/timestamp1
#		else
#			echo "timestamp of $1 is lost"
#		fi
#		if [ -e /var/tmp/timestamp2 ];then
#			cat /var/tmp/timestamp2 | xargs touch $2 -t
#			rm -f /var/tmp/timestamp2
#		else
#			echo "timestamp of $2 is lost"
#		fi
#	elif [ ! -s $1 ];then
#		mcputil read 60 $1.lz 61 /var/tmp/timestamp
#		/usr/bin/lzma -d $1.lz -n $1
#		rm -f $1.lz
#		if [ -e /var/tmp/timestamp ];then
#			cat /var/tmp/timestamp | xargs touch $1 -t
#			rm -f /var/tmp/timestamp
#		else
#			echo "timestamp of $1 is lost"
#		fi
#	fi
#else
	sys atmc
	if [ -e /tmp/teConfigFlag ]; then
		teConfigFlag=`cat /tmp/teConfigFlag`
		if [ $teConfigFlag == 1 ]; then
			if [ $# -eq 2 ]; then 
				if [ "$MLD_APPS_ENABLE_OPENSSL_111" != "" ]; then
					#openssl aes-256-cbc -md MD5 -k $2 -d -in /usr/etc/smt.cfg -out /var/pdm/config.xml
					openssl aes-256-cbc -k $2 -d -in /etc/smt.cfg -out /var/pdm/config.xml
				else
					openssl aes-256-cbc -k $2 -d -in /usr/etc/smt.cfg -out /var/pdm/config.xml
				fi
				cp -a /var/pdm/config.xml /var/pdm/backup.xml
				exit 0
			else
				cp -a /usr/etc/smt.cfg /var/pdm/config.xml
				exit 0
			fi
		else
			echo "teconfig = $teConfigFlag"
		fi
	fi	

	if [ ! -s $1 ];then
		/sbin/mcputil read 60 $1.lz 61 /var/tmp/timestamp
		/usr/bin/lzma -d $1.lz -n $1
		cp -a $1 /var/pdm/backup.xml
		rm -f $1.lz
		if [ -e /var/tmp/timestamp ];then
			cat /var/tmp/timestamp | xargs touch $1 -t
			rm -f /var/tmp/timestamp
		else
			echo "timestamp of $1 is lost" >> /var/log/syslog.log
		fi
	fi
#fi
