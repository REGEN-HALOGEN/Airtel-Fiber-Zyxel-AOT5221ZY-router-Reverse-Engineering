#!/bin/sh

GREP="/bin/grep"
USR_CONFIG_ERR=200
isXML=`grep xml $1 | grep version`

if [ "$isXML" != "" ]; then
	echo "User Configuration OK!!!"
	exit 0
else
	echo "User Configuration Error!!!"
	exit $USR_CONFIG_ERR
fi
