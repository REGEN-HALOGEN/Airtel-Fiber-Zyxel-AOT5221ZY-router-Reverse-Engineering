#!/bin/sh

TIMEOUT_SEC=$1
CHAIN=${2:-'HELP_DESK'}

SHADOW_ORIG="/etc/shadow"
SHADOW_TEMP="/var/shadow.tmp"
CHK_SEC=5
TIMEOUT=$TIMEOUT_SEC

CHK_CMD="iptables -v -x -L $CHAIN"
CMD1="iptables -F $CHAIN; iptables -t nat -F $CHAIN"
CMD2="ccctest -f /var/restore_helpdesk.ccc; mv $SHADOW_TEMP $SHADOW_ORIG"

if [ "$CHK_SEC" = "" ]; then
	echo "Usage: $0 <check interval(sec)> [chain]"
	exit 1
fi

CHK_VAR1=`$CHK_CMD`

CHK_COUNT=0
while [ $TIMEOUT -ge $CHK_SEC ]; do
	CHK_COUNT=$(($CHK_COUNT+1))
	sleep $CHK_SEC
	#echo "Checking Chain $CHAIN activity : $CHK_COUNT times"
	
	CHK_VAR2=`$CHK_CMD`

	#echo "***CHK_VAR1[$CHK_VAR1]"
	#echo "***CHK_VAR2[$CHK_VAR2]"

	if [ "$CHK_VAR1" = "$CHK_VAR2" ]; then
		TIMEOUT=$(($TIMEOUT-$CHK_SEC))
		#echo "--Session inactive, decrease timeout[$TIMEOUT]"
	else
		# there is activity, continue to check
		echo "--Session active, reset timeout"
		CHK_VAR1=$CHK_VAR2
		TIMEOUT=$TIMEOUT_SEC
	fi
done

# time-out command and exit
echo "--Session timeout execute"
echo "---1. [$CMD1]"
echo "---2. [$CMD2]"
sh -c "$CMD1"
sh -c "$CMD2"
exit 0
