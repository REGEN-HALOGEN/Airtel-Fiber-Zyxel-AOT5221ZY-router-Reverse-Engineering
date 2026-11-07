#!/bin/sh

pon_mode="PON_MODE=1" #1:GPON, 2:EPON, 3:Fiber
if [ -d /proc/rg  ]; then
	drvMode=1
elif [ -d /proc/fc ]; then
	drvMode=2
else
	drvMode=0
fi
if [ "$pon_mode" == "PON_MODE=1" ]; then
	dualMgmt=1 #0:Disable, 1:Enable
    if [ -f  /lib/modules/omcidrv.ko ]; then
        insmod /lib/modules/omcidrv.ko
        if [ "$drvMode" = "0" ]; then
			echo "Warning no exist rtk platform"
		else
			if [ "$drvMode" = "1" ]; then
				if [ -f /lib/modules/pf_ca8279.ko ]; then
					insmod /lib/modules/pf_ca8279.ko
				else
					echo "Warning no exist rg platform"
				fi
			elif [ "$drvMode" = "2" ]; then
				pon_speed=0 #0:GPON(0x03), 1:XGPON1(0x04), 2:XGSPON(0x05)
				if [ -f /lib/modules/pf_rt_fc.ko ]; then
					insmod /lib/modules/pf_rt_fc.ko pon_speed=$pon_speed
				else
					echo "Warning no exist fc platform"
				fi
			else
				echo "Warning undefined $drvMode value"
			fi
			if [ "$dualMgmt" == "1" ]; then
				if [ -f /etc/rtk_tr142.sh ]; then
					/etc/rtk_tr142.sh
				else
					echo "warning no exit rtk_tr142.sh"
				fi
			fi
		fi
    else
        echo "Warning no insert OMCI module in GPON mode"
    fi
fi

