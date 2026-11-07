#!/bin/sh

sleep 60

echo "========================================== CCC_INFO ===" > /dev/console

TE_Mode=`sys atsh | grep "TE Mode" | awk -F ': ' '{print $2}'`
echo "TE_Fiag             : $TE_Mode" > /dev/console
		
ccc_mr_process=`ps | grep ccc_mr | grep /bin | awk -F ' ' '{print $5}'`
ccc_mr_Level=`ps | grep ccc_mr | grep /bin | awk -F ' ' '{print $7}'`
if [ ! -z "$ccc_mr_process" ]; then
	echo "CCC_MR              : OK [$ccc_mr_Level]" > /dev/console
else
	echo "CCC_MR              : FAILED" > /dev/console
fi
		
ccc_das_process=`ps | grep ccc_das | grep /bin | awk -F ' ' '{print $5}'`
ccc_das_Level=`ps | grep ccc_das | grep /bin | awk -F ' ' '{print $7}'`
if [ ! -z "$ccc_das_process" ]; then
	echo "CCC_DAS             : OK [$ccc_das_Level]" > /dev/console
else
	echo "CCC_DAS             : FAILED" > /dev/console
fi
		
ccc_be_process=`ps | grep ccc_be | grep /bin | awk -F ' ' '{print $5}'`
ccc_be_Level=`ps | grep ccc_be | grep /bin | awk -F ' ' '{print $7}'`
if [ ! -z "$ccc_be_process" ]; then
	echo "CCC_BE              : OK [$ccc_be_Level]" > /dev/console
else
	echo "CCC_BE              : FAILED" > /dev/console
fi

echo "=======================================================" > /dev/console
