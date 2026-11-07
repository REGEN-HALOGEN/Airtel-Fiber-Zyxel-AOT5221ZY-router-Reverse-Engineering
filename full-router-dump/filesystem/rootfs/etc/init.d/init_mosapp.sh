APPNAME=mosapp
start()
{
	gponsn=`cat /var/devinfo/gponSN`
	gponpw=`cat /var/fwinfo/registrationID`
	SLIDenable=`cat /var/fwinfo/isRegidEnable`
	#If not use SLID authentication then use LOID authentication.
	if [ "$SLIDenable" == "0" ];then
		#Huawei OLT uses last 10 LOID characters as password when do LOID authentication.
		LOID=`cat /var/fwinfo/LOID | tail -c 10`
		if [ "$LOID" == "" ];then
			mosapp -s $gponsn -p $gponpw -m router &
		else
			mosapp -s $gponsn -p $LOID -m router &
		fi
	else
		mosapp -s $gponsn -p $gponpw -m router &
	fi
	echo "router" > /proc/omci/devMode
}

stop()
{
	echo "This module should not be removed"
}

restart()
{
	stop
	start
}

case "$1" in
	start)
		echo "Starting $APPNAME"
		start
		;;
	stop)
		echo "This APP($APPNAME) should not be stopped"
		;;
	restart)
		echo "This APP($APPNAME) should not be restarted"
		;;
	*)
		echo "Usage: $0 {start|stop|restart}" >&2
		exit 1
		;;
esac
exit 0
