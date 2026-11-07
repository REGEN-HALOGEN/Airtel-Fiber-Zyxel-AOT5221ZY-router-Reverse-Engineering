#!/bin/sh

export PATH=/home/bin:/home/scripts:/opt/bin:/bin:/sbin:/usr/bin:/usr/sbin
export LD_LIBRARY_PATH=/usr/lib/MSTC:/lib/MSTC:/lib/public:/lib/private:/usr/lib:/lib:/usr/lib/ebtables:/usr/lib/iptables


# QTN workaround solution
if [ -f /bin/soniq_start_stop_daemon ] ; then
	/bin/soniq_start_stop_daemon &
fi

PROCESS="/bin/zywifid_run.sh"
case "$1" in
	start)
		killall ${PROCESS##*/}
		exec ${PROCESS} &
		exit 0
		;;
		
	stop)
		killall ${PROCESS##*/}
		exit 0
		;;	

	*)
		echo "$0: unrecognized option $1"
		exit 1
		;;

esac

