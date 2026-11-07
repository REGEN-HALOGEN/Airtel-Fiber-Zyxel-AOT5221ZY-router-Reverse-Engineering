#!/bin/sh

### Executable variable ###
UTL_VER=0.0.1
EXTRACT_FB=/sbin/extract_feature_bit_${UTL_VER}
CHK_CHKSUM=/sbin/check_chksum_${UTL_VER}
EXTRACT_IMAGE=/sbin/extract_image_${UTL_VER}
SETENV=/sbin/fw_setenv
PRINTENV=/sbin/fw_printenv
RM=/bin/rm
MTD_DEBUG=/sbin/mtd_debug

### Temporary file directory ###
BOOT_HDR_FILE="/tmp/upload/bootimage.bin"

### Sciprts to check if device is in busy status ###
DEV_BUSY_CHECK_DIR=/usr/sbin/checkbusy/
FW_QUEUE_DIR=/var/spool/fw/

# This varialbe should be synchrnoise with .h file
IMG_TYPE_BOOTBASE=a5

RAS_DIR=/tmp/fwdir
HDR_INFO=$RAS_DIR/hdr_info.txt
BOOT_FILE=$RAS_DIR/uboot
STARTER_FILE=$RAS_DIR/starter
CFG_FILE=$RAS_DIR/cfg

BOOTBASE_VER=bootloaderVer

CFG_MTD=`cat /proc/mtd | grep cfg | cut -d ':' -f 1 | sed s/mtd//`

LINE_SEP="==============================================================================="
LINE_SEP2="-------------------------------------------------------------------------------"

### Other init variable ###
DEVICE=/dev/
PRINT_NULL=/dev/null

# the following value is hex
IMG_TYPE_KERNEL=10
IMG_TYPE_KERNEL_WITH_ROOTFS=11
IMG_TYPE_ROOTFS=1
IMG_TYPE_EXTFS=2

# Define Error Code Here
CHECKSUM_FAIL=100
MODEL_NUN_NOT_MATCH=101
MAGIC_NUN_INCORRECT=102
EXTRACT_FILE_ERR=103
DEVICE_IS_BUSY_ERR=104

# set state and LED

# Print firmware upgrade information
printScreen()
{
        bool=0
        while [ "$bool" != "1" ]
        do
                tmp=`ps | grep flashcp`
                tmp=`echo "$tmp" | grep sbin`
		#echo "tmp=$tmp"
                if [ "$tmp" != "" ]; then
                        printf "."
                        #sleep 1
                else
                        bool=1
                fi
        done
}


# run here while firmware file can't pass verification
cleanup ()
{
	echo "Clean firmware file"
	rm -rf $BOOT_HDR_FILE > $PRINT_NULL 2>&1
	rm $BOOT_HDR_FILE
}


#Bootbase
writeBoot()
{
	# If bootbase does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	echo $LINE_SEP
	echo "Wirte Boot Image : uboot0"
	echo "ubiformat $1 to $DEVICE$MTD_BOOT0"
	/sbin/ubiformat -s 512 -y $DEVICE$MTD_BOOT0 -f $1
	echo $LINE_SEP2

	echo $LINE_SEP
	echo "Wirte Boot Image : uboot1"
	echo "ubiformat $1 to $DEVICE$MTD_BOOT1"
	/sbin/ubiformat -s 512 -y $DEVICE$MTD_BOOT1 -f $1
	echo $LINE_SEP2
	#printScreen

}

#starter
writeStarter()
{
	# If bootbase does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	echo $LINE_SEP
	echo "$MTD_DEBUG erase starter $DEVICE$MTD_STARTER"
	$MTD_DEBUG erase $DEVICE$MTD_STARTER 0 0x100000
	echo "Wirte Boot Image : starter"
	echo "$MTD_DEBUG write $1 to $DEVICE$MTD_STARTER"
	$MTD_DEBUG write $DEVICE$MTD_STARTER 0 0x100000 $1
	echo $LINE_SEP2
	#printScreen

}

#cfg
writeCfg()
{
	# If bootbase does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	echo $LINE_SEP
	echo "Detach $DEVICE$MTD_CFG"
	/sbin/ubidetach /dev/ubi_ctrl -m $CFG_MTD
	echo "Wirte Boot Image : cfg"
	echo "ubiformat $1 to $DEVICE$MTD_CFG"
	/sbin/ubiformat -s 512 -y $DEVICE$MTD_CFG -f $1
	echo "Attach $DEVICE$MTD_CFG"
	/sbin/ubiattach /dev/ubi_ctrl -m $CFG_MTD
	echo $LINE_SEP2
	#printScreen

}

case $1 in
	# Extract image from ras.bin
	"extract")
		# Clean cache, free memory space
		echo '1' > /proc/sys/vm/drop_caches

		result=`$EXTRACT_IMAGE -i $BOOT_HDR_FILE`
		if [ "$result" != "success" ]; then
			cleanup
			exit $EXTRACT_FILE_ERR
		else
			exit 0
		fi
		;;
	# Do checksum & product model number check & device status check
	"check")
		# 2. Check Magic number number secondly, feature bit 5~8
		magic_number="0ee1dead"
		fw_magic_number=`$EXTRACT_FB -i $BOOT_HDR_FILE -s 5 -e 8`
		if [ "$magic_number" == "$fw_magic_number" ]; then
			echo "Magic Number Correct..."
		else
			echo "Magic Number Incorrect(Not a firmware)..."
			#cleanup
			exit $MAGIC_NUN_INCORRECT
		fi
	
		# 3. Check product model number first, feature bit 1~2
		fw_model=`$EXTRACT_FB -i $BOOT_HDR_FILE -s 1 -e 2`
		uboot_model=`$PRINTENV -n productModelNum`
		#echo $fw_model
		#echo $uboot_model
		if [ "$fw_model" == "$uboot_model" ]; then
			echo "Product Model Match..."
		else
			echo "Product Model Number Unmatch..."
			cleanup
			exit $MODEL_NUN_NOT_MATCH
		fi	

		# 4. Check checksum finally
		result=`$CHK_CHKSUM -i $BOOT_HDR_FILE`
		if [ "$result" != "success" ]; then
			echo "Checksum Validation Fails..."
			cleanup
			exit $CHECKSUM_FAIL
		else
			echo "Checksum Validation Success..."
		fi

		exit 0
		;;
	"update_ENV")
			bootbaseVer=`cat $HDR_INFO | grep $BOOTBASE_VER | cut -d ' ' -f 2`
			if [ "$bootbaseVer" != "" ]; then
				echo "bootbase version: $bootbaseVer"
				$SETENV bootloaderVer "$bootbaseVer" > $PRINT_NULL
			fi
		;;
	"write_flash")
		# 1. Get MTD partition information
		#/sbin/cfg_util -m /dev/ubi1_0 -r
		#ACTIVE_IMAGE=$?
		#UBOOT_IMAGE=$(($ACTIVE_IMAGE>>0))
		#UBOOT_IMAGE=$(($UBOOT_IMAGE&1))
		MTD_BOOT0=`cat /proc/mtd | grep uboot0 | cut -d ':' -f 1`
		MTD_BOOT1=`cat /proc/mtd | grep uboot1 | cut -d ':' -f 1`
		MTD_STARTER=`cat /proc/mtd | grep starter | cut -d ':' -f 1`
		MTD_CFG=`cat /proc/mtd | grep cfg | cut -d ':' -f 1`
		#MTD_BOOTBASE=`cat /proc/mtd | grep uBoot | grep -v uBoot2 | cut -d ':' -f 1`
		#echo $MTD_KERNEL
		#echo $MTD_ROOTFS
		#echo $MTD_ROOTFS_ETC


		# Program flash for bootbase		
		writeBoot $BOOT_FILE
		writeStarter $STARTER_FILE
		writeCfg $CFG_FILE

		return 0
		;;
	"reboot")
		reboot
		;;
	*)
		echo "Unkwnon command, should be extract | check | write_flash | update_ENV | reboot "
		;;
esac
exit 0

