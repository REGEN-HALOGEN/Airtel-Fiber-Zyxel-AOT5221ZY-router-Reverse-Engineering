#!/bin/sh

LTE_MODULE_NAME=""

check_id()
{
   if [ ! -e /proc/bus/usb/devices ]; then
      return 0
   fi
   
   VEND_ID=$1
   PROD_ID=$2
   CHECK_VEND=`grep P: /proc/bus/usb/devices | awk '{print $2}' | grep -i $VEND_ID | wc -l`
   CHECK_PROD=`grep P: /proc/bus/usb/devices | awk '{print $3}' | grep -i $PROD_ID | wc -l`
   if [ "$CHECK_VEND" -gt "0" ] && [ "$CHECK_PROD" -gt "0" ]; then
      return 1
   else
      return 0
   fi
}

# List of all supported LTE Modules
check_all_supported_lte_modules()
{
   # Sierra MC7710 (QMI)
   check_id 1199 68a2
   if [ "$?" == "1" ]; then
      LTE_MODULE_NAME="MC7710_QMI"
      return 1
   fi

   # Sierra MC7710 (DIP)
   check_id 1199 68a3
   if [ "$?" == "1" ]; then
      LTE_MODULE_NAME="MC7710_DIP"
      return 1
   fi

   # Novatel E362
   check_id 1410 9010
   if [ "$?" == "1" ]; then
      LTE_MODULE_NAME="E362"
      return 1
   fi
   
   # Altair ALT3100 HOSTLESS
   check_id 216f 0043
   if [ "$?" == "1" ]; then
      LTE_MODULE_NAME="ALT3100_HOSTLESS"
      return 1
   fi   
   
   return 0
}

COUNTER=0
while [ "$COUNTER" -lt "12" ]
do
   check_all_supported_lte_modules
   if [ "$?" == "1" ]; then
      break
   fi
   sleep 5
   COUNTER=$((COUNTER+1))
done

echo -n "$LTE_MODULE_NAME" > /tmp/lte_module_name.tmp
