#!/bin/sh /etc/rc.common
# Copyright (C) 2006 OpenWrt.org

PIUBI_PARTITION=piubi
DEFAULT_APP_PARTITION_SIZE=200000
DEFAULT_MRDCERT_PARTITION_SIZE=512
DEFAULT_ROMD_PARTITION_SIZE=512

DEFAULT_APP_MOUNT_POINT=/var/app

function mk_ubi_vol() {
	local ubi_number=$1
	local vol_name=$2
	local default_vol_size=$3
	local vol_desired_num=0
	local vol=`grep '^'${vol_name}'$' /sys/class/ubi/ubi${ubi_number}_*/name`

	if [ ! -z $vol ]; then 
		vol=${vol%$vol_name}
		vol=${vol//ubi${ubi_number}_/}
		vol_desired_num=${vol//[!0-9]/}
		echo "Volume ${vol_name} is exist at ubi${ubi_number} !!!!"
	else
		if [ "${default_vol_size}" != "max" ]
		then
			ubimkvol /dev/ubi${ubi_number} -s ${default_vol_size}KiB -N ${vol_name} 2>/dev/null
		else
			ubimkvol /dev/ubi${ubi_number} -m -N ${vol_name} 2>/dev/null
		fi
		if [ $? -ne 0 ];then
			echo "create VOL:${vol_name} failure!!!!"
			return 1;
		fi
		echo "Create new volume ${vol_name} at ubi${ubi_number} !!!!"
	fi

}

function check_pipartition() {
	# get MTD number by name
	if MTD=`grep $PIUBI_PARTITION /proc/mtd`;
	then
	MTD=${MTD/mtd/}; # replace "mtd" with nothing
	MTD=${MTD/:*/}; # replace ":*" (trailing) with nothing
	fi

	if [ "$MTD" != "" ] 
	then
		echo "[$0]: $PIUBI_PARTITION partition is on MTD devide $MTD"

		# try to attach piubi partition mtd to ubi, will format automatically if empty,
		if UBI=`ubiattach -m "$MTD"`;
		then
			echo ">>>>UBI attach successfully<<<<"
		else
			echo ">>>>UBI attach fail<<<<"
			echo ">>>>Erase mtd partition $PIUBI_PARTITION<<<<"
			mtd erase /dev/mtd$MTD
			if UBI=`ubiattach -m "$MTD"`;
			then
				echo ">>>>UBI attach successfully<<<<"
			else
				echo ">>>>UBI attach fail<<<<"
				return 1;
			fi
		fi

		UBI=${UBI##*"number "}; # cut all before "number ", still need to get rid of leading space
		UBI=${UBI%%,*}; # cut all after ","
		# check and create volume "ubi_apps" with 60 Mib, then mount it.
		if mk_ubi_vol $UBI ubi_apps $DEFAULT_APP_PARTITION_SIZE; then
			echo ">>>>mount ubi_apps partition<<<<"
			mkdir -p ${DEFAULT_APP_MOUNT_POINT}
			mount -t ubifs ubi"$UBI":ubi_apps ${DEFAULT_APP_MOUNT_POINT};
		fi
		# check and create volume "ubi_mrdcert1" with 512 Kib
		if mk_ubi_vol $UBI ubi_mrdcert1 $DEFAULT_MRDCERT_PARTITION_SIZE; then
			echo ">>>>create ubi_mrdcert1 volume<<<<"
		fi
		# check and create volume "ubi_mrdcert2" with 512 Kib
		if mk_ubi_vol $UBI ubi_mrdcert2 $DEFAULT_MRDCERT_PARTITION_SIZE; then
			echo ">>>>create ubi_mrdcert2 volume<<<<"
		fi
		# check and create volume "ubi_romd" with 512 Kib
		if mk_ubi_vol $UBI ubi_romd $DEFAULT_ROMD_PARTITION_SIZE; then
			echo ">>>>create ubi_romd volume<<<<"
		fi
	else
		echo "[$0]: cannot find $PIUBI_PARTITION partition."
	fi
}

boot() {
	start
	return 0
}

start() {
	if MTD=`grep $PIUBI_PARTITION /proc/mtd`;
	then
		echo ">>>>Found piubi MTD partition<<<<"
		check_pipartition
	else
		echo ">>>>No piubi MTD partition, skip this.<<<<"
	fi
}

restart() {
	# no need to unmount partition
	return 0
}

stop() {
	return 0
}
