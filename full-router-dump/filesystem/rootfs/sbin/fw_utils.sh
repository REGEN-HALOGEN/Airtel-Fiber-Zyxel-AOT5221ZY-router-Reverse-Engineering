#!/bin/sh

### Executable variable ###
UTL_VER=0.0.1
EXTRACT_FB=/sbin/extract_feature_bit_${UTL_VER}
CHK_CHKSUM=/sbin/check_chksum_${UTL_VER}
EXTRACT_IMAGE=/sbin/extract_image_${UTL_VER}
COMPUTE_CHKSUM=/sbin/compute_checksum_${UTL_VER}
SETENV=/sbin/TLV_access
PRINTENV=/sbin/TLV_access
PRINTMRD=/sbin/mrd_access
NAND_ERASE=/usr/sbin/flash_eraseall
NAND_WRITE=/usr/sbin/nandwrite
NAND_DUMP=/usr/sbin/nanddump
RM=/bin/rm
CFG_UTIL=/sbin/cfg_util
ENDIAN=`cat /etc/MLD_Config.sh | grep MLD_APPS_CCC_TARGET_ENDIAN | cut -d '=' -f 2`
SUPPORT_DTB=`cat /etc/MLD_Config.sh | grep PI_RAS_INCLUDE_DTB | cut -d '=' -f 2`

### Temporary file directory ###
RAS_UPLOAD_FILE=$2

### Sciprts to check if device is in busy status ###
DEV_BUSY_CHECK_DIR=/usr/sbin/checkbusy/
FW_QUEUE_DIR=/var/spool/fw/

# This varialbe should be synchrnoise with .h file
IMG_TYPE_KERNEL=a1
IMG_TYPE_ROOTFS=a2
IMG_TYPE_EXTFS=a3
IMG_TYPE_BOOTEXT=a4
IMG_TYPE_BOOTBASE=a5
IMG_TYPE_DEFCONFIG=a8
IMG_TYPE_UBOOT=a6
IMG_TYPE_STARTER=bb
IMG_TYPE_CFG=cc
IMG_TYPE_ZBOOT=aa
IMG_TYPE_DTB=ab 
#IMG_TYPE_RAS=a7

RAS_DIR=/tmp/fwdir
HDR_INFO=$RAS_DIR/hdr_info.txt
KERNEL_FILE=$RAS_DIR/kernel
ROOTFS_FILE=$RAS_DIR/rootfs
ETCFS_FILE=$RAS_DIR/etcfs
BOOTEXT_FILE=$RAS_DIR/bootext
DEFCONFIG_FILE=$RAS_DIR/defconfig
USERCONFIG_FILE=$RAS_DIR/userconfig
UBOOT_FILE=$RAS_DIR/uboot
STARTER_FILE=$RAS_DIR/starter
CFG_FILE=$RAS_DIR/cfg
ZBOOT_FILE=$RAS_DIR/zboot
DTB_FILE=$RAS_DIR/dtb 
#RAS_FILE=$RAS_DIR/ras

KERNEL_VER=kernelVer
ROOTFS_VER=rootfsVer
EXTFS_VER=extfsVer
STARTER_VER=starterVer
UBOOT_VER=ubootVer
BOOTEXT_VER=bootextVer
ZBOOT_VER=zbootVer
DEFCONFIG_VER=defconfigVer
DTB_VER=dtbVer 
#RAS_VER=rasVer
FW_VERSION=zyVersion
KERNEL_CHKSUM=kernelChksum
ROOTFS_CHKSUM=rootfsChksum
EXTFS_CHKSUM=extfsChksum
UBOOT_CHKSUM=ubootChksum
BOOTEXT_CHKSUM=bootextChksum
ZBOOT_CHKSUM=zbootChksum
DEFCONFIG_CHKSUM=defconfigChksum
DTB_CHKSUM=dtbChksum 
#RAS_CHKSUM=rasChksum

KERNEL_LEN=kernelLen
ROOTFS_LEN=rootfsLen
EXTFS_LEN=extfsLen
BOOTEXT_LEN=bootextLen
ZBOOT_LEN=zbootLen
UBOOT_LEN=ubootLen
DEFCONFIG_LEN=defconfigLen
DTB_LEN=dtbLen 
#RAS_LEN=rasLen

IS_VERIFY=isVerify
NEWEST_IMAGE=newestImage
RESTORE_FLAG=restoreFlag

KERNEL_IMAGE=
ROOTFS_IMAGE=
DEFCONFIG_IMAGE=
UBOOT_IMAGE=
BOOTEXT_IMAGE=
ZBOOT_IMAGE=
DTB_IMAGE=  
#RAS_IMAGE=
DEBUG_FLAG=`$PRINTMRD debugFlag`

CFG_UTIL=/sbin/cfg_util
isRestoreEnv=0

TMP_STARTER_FILE=/tmp/starter
TMP_MRD_FILE=/tmp/mrd
TMP_STARTER_MRD_FILE=/tmp/starter_mrd
BLOCK_SIZE=131072

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
IMG_TYPE_DTB=20 

# Define Error Code Here
CHECKSUM_FAIL=100
MODEL_NUN_NOT_MATCH=101
MAGIC_NUN_INCORRECT=102
EXTRACT_FILE_ERR=103
DEVICE_IS_BUSY_ERR=104

CFG_DEV=/dev/ubi1_0

FLASHWRITE_CHKOK=1
RET=0

ZIP_TOOL=gzip
ZIP_SUFFIX=gz

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

unzipFile()
{
	/* For gzip compressed images */
	ZIP_TOOL=gzip
	ZIP_SUFFIX=gz
	mv -f $1 $1.$ZIP_SUFFIX
	result=`echo $?`
	if [ "$result" != "0" ]; then
		echo "mv -f $1 $1.$ZIP_SUFFIX failed!!!" > /dev/console
		# enable H/W monitor watchdog
		/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
		/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
		return $EXTRACT_FILE_ERR
	fi

	echo "Decompressing the image : $1.$ZIP_SUFFIX..." > /dev/console
	$ZIP_TOOL -df $1.$ZIP_SUFFIX
	result=`echo $?`
	if [ "$result" != "0" ]; then
		echo "Not a $ZIP_TOOL compressed image : $1.$ZIP_SUFFIX!!!" > /dev/console
		mv -f $1.$ZIP_SUFFIX $1
	else
		echo "Decompressing image OK" > /dev/console
		#rm -f $1.$ZIP_SUFFIX
	fi
	/* For gzip compressed images End */

	/* For lzma compressed images */
	if [ "$result" != "0" ]; then
		ZIP_TOOL=lzma
		ZIP_SUFFIX=lzma
		mv -f $1 $1.$ZIP_SUFFIX
		result=`echo $?`
		if [ "$result" != "0" ]; then
			echo "mv -f $1 $1.$ZIP_SUFFIX failed!!!" > /dev/console
			# enable H/W monitor watchdog
			/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			return $EXTRACT_FILE_ERR
		fi

		echo "Decompressing the image : $1.$ZIP_SUFFIX..." > /dev/console
		$ZIP_TOOL -df $1.$ZIP_SUFFIX
		result=`echo $?`
		if [ "$result" != "0" ]; then
			echo "Not a $ZIP_TOOL compressed image : $1.$ZIP_SUFFIX!!!" > /dev/console
			mv -f $1.$ZIP_SUFFIX $1
		else
			echo "Decompressing image OK" > /dev/console
			#rm -f $1.$ZIP_SUFFIX
		fi
	fi
	/* For lzma compressed images End */

	return 0
}

# run here while firmware file can't pass verification
cleanup ()
{
	echo "Clean firmware files"
	echo '1' > /proc/sys/vm/drop_caches
	rm -rf $RAS_UPLOAD_FILE > $PRINT_NULL 2>&1
}

nandSave()
{
	echo " write $1 to $2" > /dev/console
	$NAND_ERASE $2 > /dev/console
	$NAND_WRITE -p $2 $1 > /dev/console
	RET=$?
	FLASHWRITE_CHKOK=1
	if [ $RET != "0" ]; then
		FLASHWRITE_CHKOK=0
	fi
	echo "Result = $RET" > /dev/console
	
}

#Rootfs_etc
writeExtfs()
{
	# If rootfs-etc does not exist, do not progam flash
	if [ ! -f $1 ]; then
		return
	fi
	unzipFile $1
	RET=$?
	if [ $RET != "0" ]; then
      	FLASHWRITE_CHKOK=0
      	return
	fi

	echo $LINE_SEP
	echo "Wirte RootFS_ETC Image"
        echo "flashcp $1 to $DEVICE$MTD_ROOTFS_ETC"
	/sbin/flash_eraseall -j -q $DEVICE$MTD_ROOTFS_ETC
	RET=$?
	 FLASHWRITE_CHKOK=1
     if [ $RET != "0" ]; then
      	FLASHWRITE_CHKOK=0
     fi
     echo "Result = $RET" > /dev/console
     /sbin/flashcp -v $1 $DEVICE$MTD_ROOTFS_ETC
     RET=$?
      FLASHWRITE_CHKOK=1
      if [ $RET != "0" ]; then
       	FLASHWRITE_CHKOK=0
      fi
      echo "Result = $RET" > /dev/console
	echo $LINE_SEP2
	#printScreen
}
# Rootfs
writeRootfs()
{
	# If rootfs does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
		#FLASHWRITE_CHKOK=0
		#return
	#fi
	echo $LINE_SEP > /dev/console
	echo "Wirte RootFS Image" > /dev/console
	MTD_POINT=$DEVICE$MTD_ROOTFS
	nandSave $1 $MTD_POINT 
	echo $LINE_SEP2 > /dev/console
	#printScreen
}

# Kernel
writeKernel()
{
	# If kernel does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
		#FLASHWRITE_CHKOK=0
		#return
	#fi
	echo $LINE_SEP > /dev/console
	echo "Wirte Kernel Image" > /dev/console
	MTD_POINT=$DEVICE$MTD_KERNEL
	nandSave $1 $MTD_POINT 
	echo $LINE_SEP2 > /dev/console
	#printScreen
}

#Bootext
writeBootext()
{
	# If bootext does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	
	if [ -z "$MTD_BOOTEXT" ]; then 
		echo "MTD_BOOTEXT is empty" > /dev/console
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
		#FLASHWRITE_CHKOK=0
		#return
	#fi

	echo $LINE_SEP > /dev/console
	echo "Wirte Bootext Image" > /dev/console
	MTD_POINT=$DEVICE$MTD_BOOTEXT
	nandSave $1 $MTD_POINT 
	echo $LINE_SEP2 > /dev/console
	#printScreen
}

# defconfig
writeDefconfig()
{
	# If defconfig does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
      	#FLASHWRITE_CHKOK=0
      	#return
	#fi
	echo $LINE_SEP
	echo "Wirte Defconfig Image"
        echo " write $1 to $DEVICE$MTD_DEFCONFIG"
        $NAND_ERASE $DEVICE$MTD_DEFCONFIG > /dev/console
	$NAND_WRITE -p $DEVICE$MTD_DEFCONFIG $1 > /dev/console
        RET=$?
        FLASHWRITE_CHKOK=1
        if [ $RET != "0" ]; then
        	FLASHWRITE_CHKOK=0
        fi
        echo "Result = $RET" > /dev/console
	echo $LINE_SEP2
	#printScreen
}

# userconfig
writeUserconfig()
{
	# If userconfig does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
      	#FLASHWRITE_CHKOK=0
      	#return
	#fi
	echo $LINE_SEP
	echo "Wirte Userconfig Image"
        echo " write $1 to $DEVICE$MTD_USERCONFIG"
        $NAND_ERASE $DEVICE$MTD_USERCONFIG > /dev/console
        $NAND_WRITE -p $DEVICE$MTD_USERCONFIG $1 > /dev/console
        RET=$?
        FLASHWRITE_CHKOK=1
        if [ $RET != "0" ]; then
        	FLASHWRITE_CHKOK=0
        fi
        echo "Result = $RET" > /dev/console
	echo $LINE_SEP2
	#printScreen
}

#Uboot
writeUboot()
{
	# If UBoot does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	
	if [ $DEBUG_FLAG = "0" ]; then
		FLASHWRITE_CHKOK=0
		return
	fi

	if [ -z "$MTD_UBOOT" ]; then 
		echo "MTD_UBOOT is empty..." > /dev/console
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
      	#FLASHWRITE_CHKOK=0
      	#return
	#fi
	echo $LINE_SEP > /dev/console
	echo "Wirte Uboot Image" > /dev/console
	MTD_POINT=$DEVICE$MTD_UBOOT
	nandSave $1 $MTD_POINT
	echo $LINE_SEP2 > /dev/console
	FLASHWRITE_CHKOK=1
	#printScreen
}

# DTB
writeDTB()
{
	# If DTB does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	echo $LINE_SEP > /dev/console
	echo "Wirte DTB Image" > /dev/console
	MTD_POINT=$DEVICE$MTD_DTB
	nandSave $1 $MTD_POINT 
	echo $LINE_SEP2 > /dev/console
}


#Uboot
writeBoot()
{
	# If starter does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	if [ $DEBUG_FLAG = "0" ]; then
		FLASHWRITE_CHKOK=0
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
      	#FLASHWRITE_CHKOK=0
      	#return
	#fi
	echo $LINE_SEP

	#============================backup the current MRD info============================
#	MTD_NUM=`cat /proc/mtd |grep -w boot|awk 'NR==1'`
#	if [ -z "$MTD_NUM" ];then 
#		echo "Error,no such MTD_NAME [boot]!!"
#		FLASHWRITE_CHKOK=0
#		return
#	fi
#	MTD_NUM=`echo "$MTD_NUM"|cut -d ':' -f 1|cut -b 4-|awk 'NR==1'`
#	MRD_SIZE=`/sbin/mrd_access mrdSize`
#	SKIP_SIZE=`expr $BLOCK_SIZE - $MRD_SIZE`
#	dd if=/dev/mtd$MTD_NUM of=$TMP_MRD_FILE skip=$SKIP_SIZE bs=1 count=$MRD_SIZE
#	dd if=$1 of=$TMP_STARTER_FILE bs=1 count=$SKIP_SIZE
#	cat $TMP_STARTER_FILE $TMP_MRD_FILE > $TMP_STARTER_MRD_FILE
#	$RM -f $TMP_STARTER_FILE $TMP_MRD_FILE
	#============================backup the current MRD info end========================

	echo "Wirte boot Image"
	/sbin/flashcp -v $1 $DEVICE$MTD_STARTER
	echo " write $1 to $DEVICE$MTD_STARTER"
#        $NAND_ERASE $DEVICE$MTD_STARTER > /dev/console
#        $NAND_WRITE -p $DEVICE$MTD_STARTER $1 > /dev/console
	RET=$?
	echo "Result = $RET" > /dev/console
	FLASHWRITE_CHKOK=1
	if [ $RET != "0" ]; then
		FLASHWRITE_CHKOK=0
		return
	fi

#	echo "Wirte backup mrd Image"
#	echo "flashcp $TMP_STARTER_MRD_FILE to $DEVICE$MTD_STARTER"
#	/sbin/flashcp -v $TMP_STARTER_MRD_FILE $DEVICE$MTD_STARTER
#	RET=$?
#	echo "Result = $RET" > /dev/console
#	FLASHWRITE_CHKOK=1
#	if [ $RET != "0" ]; then
#		FLASHWRITE_CHKOK=0
#	fi

	echo $LINE_SEP2
	#printScreen
}

#Bootext
writeZboot()
{
	# If zboot does not exist, do not program flash
	if [ ! -f $1 ]; then
		return
	fi
	#unzipFile $1
	#RET=$?
	#if [ $RET != "0" ]; then
      	#FLASHWRITE_CHKOK=0
      	#return
	#fi
	echo $LINE_SEP > /dev/console
	echo "Wirte Zboot Image" > /dev/console
	MTD_POINT=$DEVICE$MTD_ZBOOT
	nandSave $1 $MTD_POINT
	echo $LINE_SEP2 > /dev/console
	#printScreen
}

# ras
#writeRas()
#{
#	# If ras does not exist, do not program flash
#	if [ ! -f $1 ]; then
#		return
#	fi
#	#unzipFile $1
#	#RET=$?
#	#if [ $RET != "0" ]; then
#		#FLASHWRITE_CHKOK=0
#		#return
#	#fi
#	echo $LINE_SEP > /dev/console
#	echo "Wirte ras Image" > /dev/console
#	MTD_POINT=$DEVICE$MTD_RAS
#	nandSave $1 $MTD_POINT 
#	echo $LINE_SEP2 > /dev/console
#	#printScreen
#}

#######################################################################################
#  checkbusy() function will check if device is busy or not
#  It will scan all scripts under /usr/sbin/checkbusy, if any scripts under
#  /usr/sbin/checkbusy return non-zero, checkbusy will return 1 and it means device is 
#  busy now. Otherwise it will return 0
#######################################################################################
DEV_BUSY_CHECK_DIR=/usr/sbin/checkbusy/
checkbusy()
{
	for script in `ls $DEV_BUSY_CHECK_DIR`
	do
		if [ -x $DEV_BUSY_CHECK_DIR/$script ]; then
                	$DEV_BUSY_CHECK_DIR/$script
			result=$?
			if [ ! $result -eq 0 ]; then
				echo "$script says device is busy now." > /dev/console
				return 1
                        fi
		fi
	done
	echo "done" > /dev/console
	return 0
}

case $1 in
	# Extract image from ras.bin
	"extract")
		# Clean cache, free memory space
		echo 8 > /proc/sys/kernel/printk
		echo 3 > /proc/sys/vm/drop_caches

		if [ "$ENDIAN" != "BIG_ENDIAN" ]; then 
			result=`$EXTRACT_IMAGE -i $RAS_UPLOAD_FILE -W` > /dev/console
		else	
			result=`$EXTRACT_IMAGE -b -i $RAS_UPLOAD_FILE -W` > /dev/console
		fi
		echo "result=$result" 
		
		cleanup
		;;
	# Do checksum & product model number check & device status check
	"check")
		#uncompress the image
		#Check if updating the bootbase    #
		result=`$EXTRACT_IMAGE -i $RAS_UPLOAD_FILE -T`
		if [ "$result" != "success" ]; then
			echo "Check image failed!!!" > /dev/console
			exit $EXTRACT_FILE_ERR
		else
			starterVer=`cat $HDR_INFO | grep $STARTER_VER | cut -d ' ' -f 2`
			if [ "$starterVer" != "" ] && [ $DEBUG_FLAG != "1" ]; then
				echo "Check image STARTER_VER failed!!!" > /dev/console
				exit $EXTRACT_FILE_ERR
			fi
			ubootVer=`cat $HDR_INFO | grep $UBOOT_VER | cut -d ' ' -f 2`
			if [ "$ubootVer" != "" ] && [ $DEBUG_FLAG != "1" ]; then
				echo "Check image $UBOOT_VER failed!!!" > /dev/console
				exit $EXTRACT_FILE_ERR
			fi
		fi
		#Check if updating the bootbase end#

		echo 8 > /proc/sys/kernel/printk
		echo 3 > /proc/sys/vm/drop_caches

		# For gzip compressed image
		ZIP_TOOL=gzip
		ZIP_SUFFIX=gz
		mv -f $RAS_UPLOAD_FILE $RAS_UPLOAD_FILE.$ZIP_SUFFIX
		result=`echo $?`
		if [ "$result" != "0" ]; then
			echo "mv -f $RAS_UPLOAD_FILE $RAS_UPLOAD_FILE.$ZIP_SUFFIX failed!!!" > /dev/console
			exit $EXTRACT_FILE_ERR
		fi

		echo "Decompressing the image..." > /dev/console
		$ZIP_TOOL -df $RAS_UPLOAD_FILE.$ZIP_SUFFIX
		result=`echo $?`
		if [ "$result" != "0" ]; then
			echo "Not a $ZIP_TOOL compressed image!!!" > /dev/console
			mv -f $RAS_UPLOAD_FILE.$ZIP_SUFFIX $RAS_UPLOAD_FILE
		else
			echo "Decompressing image OK" > /dev/console
			#rm -f $RAS_UPLOAD_FILE.$ZIP_SUFFIX
		fi
		# For gzip compressed image End 

		# For lzma compressed image 
		if [ "$result" != "0" ]; then
			ZIP_TOOL=lzma
			ZIP_SUFFIX=lzma
			mv -f $RAS_UPLOAD_FILE $RAS_UPLOAD_FILE.$ZIP_SUFFIX
			result=`echo $?`
			if [ "$result" != "0" ]; then
				echo "mv -f $RAS_UPLOAD_FILE $RAS_UPLOAD_FILE.$ZIP_SUFFIX failed!!!" > /dev/console
				exit $EXTRACT_FILE_ERR
			fi

			echo "Decompressing the image..." > /dev/console
			$ZIP_TOOL -df $RAS_UPLOAD_FILE.$ZIP_SUFFIX
			result=`echo $?`
			if [ "$result" != "0" ]; then
				echo "Not a $ZIP_TOOL compressed image!!!" > /dev/console
				mv -f $RAS_UPLOAD_FILE.$ZIP_SUFFIX $RAS_UPLOAD_FILE
			else
				echo "Decompressing image OK" > /dev/console
				#rm -f $RAS_UPLOAD_FILE.$ZIP_SUFFIX
			fi
		fi
		# For lzma compressed image End

		# 2. Check Magic number number secondly, feature bit 5~8
		magic_number="0ee1dead"
		fw_magic_number=`$EXTRACT_FB -i $RAS_UPLOAD_FILE -s 5 -e 8`
		if [ "$magic_number" == "$fw_magic_number" ]; then
			echo "Magic Number Correct..." > /dev/console
		else
			echo "Magic Number Incorrect(Not a firmware)..." > /dev/console
			cleanup
			exit $MAGIC_NUN_INCORRECT
		fi
	
		# 3. Check product model number first, feature bit 1~2
		fw_model=`$EXTRACT_FB -i $RAS_UPLOAD_FILE -s 1 -e 2`
		uboot_model=`$PRINTMRD modelid`
		fw_tmp=$(echo $fw_model  | tr "[:upper:]" "[:lower:]"  ) 
		model_tmp=$(echo $uboot_model  | tr "[:upper:]" "[:lower:]"  )
		if [ "$fw_tmp" == "$model_tmp" ]; then
			echo "Product Model Match..." > /dev/console
		else
			echo "Product Model Number Unmatch..." > /dev/console
			cleanup
			exit $MODEL_NUN_NOT_MATCH
		fi	

		# 4. Check checksum finally
		if [ "$ENDIAN" != "BIG_ENDIAN" ]; then 
			result=`$CHK_CHKSUM -i $RAS_UPLOAD_FILE`
		else	
		result=`$CHK_CHKSUM -b -i $RAS_UPLOAD_FILE`
		fi
		if [ "$result" != "success" ]; then
			echo "Checksum Validation Fails...result=$result" > /dev/console
			cleanup
			exit $CHECKSUM_FAIL
		else
			echo "Checksum Validation Success..." > /dev/console
		fi

		exit 0
		;;
	"update_TLV")
			### Get the new image partition 
			#$CFG_UTIL -m $CFG_DEV -r
			ACTIVE_IMAGE=`$PRINTENV newestImage`

			UBOOT_IMAGE=$((!$ACTIVE_IMAGE))
			BOOTEXT_IMAGE=$((!$ACTIVE_IMAGE))
			ZBOOT_IMAGE=$((!$ACTIVE_IMAGE))
			KERNEL_IMAGE=$((!$ACTIVE_IMAGE))
			DTB_IMAGE=$((!$ACTIVE_IMAGE)) 
			ROOTFS_IMAGE=$((!$ACTIVE_IMAGE))
			DEFCONFIG_IMAGE=$((!$ACTIVE_IMAGE))
#			RAS_IMAGE=$((!$ACTIVE_IMAGE))

			MTD_UBOOT=`cat /proc/mtd | grep uboot$UBOOT_IMAGE | cut -d ':' -f 1`
			MTD_BOOTEXT=`cat /proc/mtd | grep bootext$BOOTEXT_IMAGE | cut -d ':' -f 1`
			MTD_KERNEL=`cat /proc/mtd | grep ubi_k$KERNEL_IMAGE | cut -d ':' -f 1`
			MTD_ROOTFS=`cat /proc/mtd | grep ubi_r$ROOTFS_IMAGE | cut -d ':' -f 1`
			MTD_DTB=`cat /proc/mtd | grep ubi_DTB$DTB_IMAGE | cut -d ':' -f 1`  
			
			echo "Update TLV" > /dev/console

			####### Enable TLVSaveLock to prevent keeping writing TLV partition when firmware upgrade
			$SETENV TLVSaveLock 1

#			kernelVer=`cat $HDR_INFO | grep $KERNEL_VER | cut -d ' ' -f 2`
#			if [ "$kernelVer" != "" ]; then
#				echo "Upload Image as $KERNEL_IMAGE image"
#				$SETENV newestImage $KERNEL_IMAGE > $PRINT_NULL
#				# Set this image to be non-verify image
#				$SETENV isVerify$KERNEL_IMAGE 0 > $PRINT_NULL
#			fi
			####### Verify Checksum information first
			if [ "$SUPPORT_DTB" != "" ]; then
				echo "Verify checksum in ubi_k$KERNEL_IMAGE ,ubi_r$ROOTFS_IMAGE and ubi_DTB$DTB_IMAGE correct or not." > /dev/console 
			else
			echo "Verify checksum in ubi_k$KERNEL_IMAGE and ubi_r$ROOTFS_IMAGE correct or not." > /dev/console
			fi
			kernelChksum=`cat $HDR_INFO | grep $KERNEL_CHKSUM | cut -d ' ' -f 2`
			kernelLen=`cat $HDR_INFO | grep $KERNEL_LEN | cut -d ' ' -f 2`
			if [ "$kernelChksum" != "" ]; then
				$NAND_DUMP -q -l 0x$kernelLen -f /tmp/nanddump_ubi_k$KERNEL_IMAGE /dev/$MTD_KERNEL
				computeKerChksum=`$COMPUTE_CHKSUM -l 0x$kernelLen -i /tmp/nanddump_ubi_k$KERNEL_IMAGE`				
				#rm /tmp/nanddump_ubi_k$KERNEL_IMAGE
				#Because the rm is limited from sftp session, we replace the rm to "echo "" > path".  
				echo "" > /tmp/nanddump_ubi_k$KERNEL_IMAGE

				if [ "$kernelChksum" != "$computeKerChksum" ]; then
					echo "Incorrect checksum $computeKerChksum in ubi_k$KERNEL_IMAGE!" > /dev/console
					exit $CHECKSUM_FAIL
				else
					echo "File kernel checksum: $kernelChksum matches ubi_k$KERNEL_IMAGE checksum: $computeKerChksum" > /dev/console
				fi
			fi

			rootfsChksum=`cat $HDR_INFO | grep $ROOTFS_CHKSUM | cut -d ' ' -f 2`
			rootfsLen=`cat $HDR_INFO | grep $ROOTFS_LEN | cut -d ' ' -f 2`
			if [ "$rootfsChksum" != "" ]; then
				$NAND_DUMP -q -l 0x$rootfsLen -f /tmp/nanddump_ubi_r$ROOTFS_IMAGE /dev/$MTD_ROOTFS
				computeRootfsChksum=`$COMPUTE_CHKSUM -l 0x$rootfsLen -i /tmp/nanddump_ubi_r$ROOTFS_IMAGE`
				#rm /tmp/nanddump_ubi_r$ROOTFS_IMAGE
				#Because the rm is limited from sftp session, we replace the rm to "echo "" > path".  
				echo "" > /tmp/nanddump_ubi_r$ROOTFS_IMAGE				
				if [ "$rootfsChksum" != "$computeRootfsChksum" ]; then
					echo "Incorrect checksum $computeRootfsChksum in ubi_r$ROOTFS_IMAGE!" > /dev/console
					exit $CHECKSUM_FAIL
				else
					echo "File rootfs checksum: $rootfsChksum matches ubi_r$ROOTFS_IMAGE checksum: $computeRootfsChksum" > /dev/console
				fi
			fi

			if [ "$SUPPORT_DTB" != "" ]; then
				dtbChksum=`cat $HDR_INFO | grep $DTB_CHKSUM | cut -d ' ' -f 2`
				dtbLen=`cat $HDR_INFO | grep $DTB_LEN | cut -d ' ' -f 2`
				if [ "$dtbChksum" != "" ]; then
					$NAND_DUMP -q -l 0x$dtbLen -f /tmp/nanddump_ubi_DTB$DTB_IMAGE /dev/$MTD_DTB
					computeDTBChksum=`$COMPUTE_CHKSUM -l 0x$dtbLen -i /tmp/nanddump_ubi_DTB$DTB_IMAGE`
					echo "" > /tmp/nanddump_ubi_DTB$DTB_IMAGE				
					if [ "$dtbChksum" != "$computeDTBChksum" ]; then
						echo "Incorrect checksum $computeDTBChksum in ubi_DTB$DTB_IMAGE!" > /dev/console
						exit $CHECKSUM_FAIL
					else
						echo "File dtb checksum: $dtbChksum matches ubi_DTB$DTB_IMAGE checksum: $computeDTBChksum" > /dev/console
					fi
				fi
			fi
			####### Make sure UBI upd_marker is reset to 0
			if [ -x "$(which ubinfo)" ]; then
				if [ "$SUPPORT_DTB" != "" ]; then				
					echo "Make sure ubi_k$KERNEL_IMAGE ,ubi_r$ROOTFS_IMAGE and ubi_DTB$DBT_IMAGE upd_marker are reset to 0" > /dev/console
				else
				echo "Make sure ubi_k$KERNEL_IMAGE and ubi_r$ROOTFS_IMAGE upd_marker are reset to 0" > /dev/console
				fi
				kernelUBIDevice='ubi0_'`ubinfo -d 0 -N ubi_k$KERNEL_IMAGE |grep "Volume ID" | awk '{print $3}'`
				rootfsUBIDevice='ubi0_'`ubinfo -d 0 -N ubi_r$ROOTFS_IMAGE |grep "Volume ID" | awk '{print $3}'`
				dtbUBIDevice='ubi0_'`ubinfo -d 0 -N ubi_DTB$DTB_IMAGE |grep "Volume ID" | awk '{print $3}'`
				
				checkIndex=0
				while [ $checkIndex != 10 ]
				do
					kernelUpdMarker=`cat /sys/devices/virtual/ubi/ubi0/$kernelUBIDevice/upd_marker`
					rootfsUpdMarker=`cat /sys/devices/virtual/ubi/ubi0/$rootfsUBIDevice/upd_marker`
					dtbUpdMarker=`cat /sys/devices/virtual/ubi/ubi0/$dtbUBIDevice/upd_marker`
					if [ "$SUPPORT_DTB" != "" ]; then
						if [ "$kernelUpdMarker" != '0' ] || [ "$rootfsUpdMarker" != '0' ] || [ "$dtbUpdMarker" != '0' ]; then
							if [ $checkIndex != 9 ]; then
								echo "ubi_k$KERNEL_IMAGE upd_marker is $kernelUpdMarker and ubi_r$ROOTFS_IMAGE upd_marker is $rootfsUpdMarker ubi_DTB$DTB_IMAGE upd_marker is $dtbUpdMarker" > /dev/console
								echo "Wait for all upd_marker are reset to 0..." > /dev/console
							else
								echo "ubi_k$KERNEL_IMAGE upd_marker is $kernelUpdMarker and ubi_r$ROOTFS_IMAGE upd_marker is $rootfsUpdMarker ubi_DTB$DTB_IMAGE upd_marker is $dtbUpdMarker" > /dev/console
								echo "upb_marker is not reset to 0. Ignore this firmware upgrade." > /dev/console
								exit $CHECKSUM_FAIL
							fi
						else
							echo "ubi_k$KERNEL_IMAGE ,ubi_r$ROOTFS_IMAGE and ubi_DTB$DTB_IMAGE upd_marker are reset to 0. Keep going." > /dev/console
							break
						fi
					else
					if [ "$kernelUpdMarker" != '0' ] || [ "$rootfsUpdMarker" != '0' ]; then
						if [ $checkIndex != 9 ]; then
							echo "ubi_k$KERNEL_IMAGE upd_marker is $kernelUpdMarker and ubi_r$ROOTFS_IMAGE upd_marker is $rootfsUpdMarker" > /dev/console
							echo "Wait for all upd_marker are reset to 0..." > /dev/console
						else
							echo "ubi_k$KERNEL_IMAGE upd_marker is $kernelUpdMarker and ubi_r$ROOTFS_IMAGE upd_marker is $rootfsUpdMarker" > /dev/console
							echo "upb_marker is not reset to 0. Ignore this firmware upgrade." > /dev/console
							exit $CHECKSUM_FAIL
						fi
					else
							echo "ubi_k$KERNEL_IMAGE and ubi_r$ROOTFS_IMAGE are reset to 0. Keep going." > /dev/console
						break
					fi
					fi
					sleep 1
					checkIndex=`expr $checkIndex + 1`
				done
			else
				echo "Not support ubinfo..." > /dev/console
			fi
			####### Update Version information
			kernelVer=`cat $HDR_INFO | grep $KERNEL_VER | cut -d ' ' -f 2`
			#kernelVer, rootfsVer, ubootVer, zbootVer is the same version
			if [ "$kernelVer" != "" ]; then
				echo "version-$KERNEL_IMAGE version: $kernelVer" > /dev/console
				$SETENV  version$KERNEL_IMAGE "$kernelVer" > $PRINT_NULL
			fi
			rootfsVer=`cat $HDR_INFO | grep $ROOTFS_VER | cut -d ' ' -f 2`
			if [ "$rootfsVer" != "" ]; then
				echo "rootfs-$ROOTFS_IMAGE version: $rootfsVer" > /dev/console
				$SETENV rootfsVer$ROOTFS_IMAGE "$rootfsVer" > $PRINT_NULL
			fi
			if [ "$SUPPORT_DTB" != "" ]; then
				dtbVer=`cat $HDR_INFO | grep $DTB_VER | cut -d ' ' -f 2`
				if [ "$dtbVer" != "" ]; then
					echo "dtb-$DTB_IMAGE version: $dtbVer" > /dev/console
					$SETENV dtbVer$DTB_IMAGE "$dtbVer" > $PRINT_NULL
				fi
			fi
#			confVer=`cat $HDR_INFO | grep $EXTFS_VER | cut -d ' ' -f 2`
#			if [ "$confVer" != "" ]; then
#				echo "rootfs-etc-$NEW_IMAGE version: $confVer"
#				$SETENV confVer$NEW_IMAGE "$confVer" > $PRINT_NULL
#			fi
#			bootextVer=`cat $HDR_INFO | grep $BOOTEXT_VER | cut -d ' ' -f 2`
#			if [ "$bootextVer" != "" ]; then
#				echo "bootext-$BOOTEXT_IMAGE version: $bootextVer"
#				$SETENV bootextVer$BOOTEXT_IMAGE "$bootextVer" > $PRINT_NULL
#			else
#				TMP_BOOTEXT_IMAGE=$((!$BOOTEXT_IMAGE))
#				echo "bootext-$TMP_BOOTEXT_IMAGE version: $kernelVer"
#				$SETENV bootextVer$TMP_BOOTEXT_IMAGE "$kernelVer" > $PRINT_NULL
#			fi
#			zbootVer=`cat $HDR_INFO | grep $ZBOOT_VER | cut -d ' ' -f 2`
#			if [ "$zbootVer" != "" ]; then
#				echo "zboot-$ZBOOT_IMAGE version: $zbootVer"
#				$SETENV zbootVer$ZBOOT_IMAGE "$zbootVer" > $PRINT_NULL
#			else
#				TMP_ZBOOT_IMAGE=$((!$ZBOOT_IMAGE))
#				echo "zboot-$TMP_ZBOOT_IMAGE version: $kernelVer"
#				$SETENV zbootVer$TMP_ZBOOT_IMAGE "$kernelVer" > $PRINT_NULL
#			fi
#			defconfigVer=`cat $HDR_INFO | grep $DEFCONFIG_VER | cut -d ' ' -f 2`
#			if [ "$defconfigVer" != "" ]; then
#				echo "defconfig-$DEFCONFIG_IMAGE version: $defconfigVer"
#				$SETENV  defconfigVer$DEFCONFIG_IMAGE "$defconfigVer" > $PRINT_NULL
#			fi
			fw_version=`cat $HDR_INFO | grep $FW_VERSION | cut -d ' ' -f 2 | awk 'NR==1'`
			if [ "$fw_version" != "" ]; then
			#	echo "fw_version-$KERNEL_IMAGE version: $fw_version" > /dev/console
				$SETENV  fw_version$KERNEL_IMAGE "$fw_version" > $PRINT_NULL
			fi
			####### Update Checksum information
			if [ "$kernelChksum" != "" ]; then
				echo "kernel-$KERNEL_IMAGE checksum: $kernelChksum" > /dev/console
				$SETENV kernelChecksum$KERNEL_IMAGE "$kernelChksum" > $PRINT_NULL
			fi
			if [ -z "$MTD_UBOOT" ]; then 
				echo "TLV_Write: MTD_UBOOT is empty" > /dev/console
			else
				ubootChksum=`cat $HDR_INFO | grep $UBOOT_CHKSUM | cut -d ' ' -f 2`
				if [ "$ubootChksum" != "" ]; then
					echo "uboot-$UBOOT_IMAGE checksum: $ubootChksum" > /dev/console
					$SETENV ubootChecksum$UBOOT_IMAGE "$ubootChksum" > $PRINT_NULL
				fi
				ubootLen=`cat $HDR_INFO | grep $UBOOT_LEN | cut -d ' ' -f 2`
				if [ "$ubootLen" != "" ]; then
					echo "uboot-$UBOOT_IMAGE Len: $ubootLen" > /dev/console
					$SETENV ubootLen$UBOOT_IMAGE "0x$ubootLen" > $PRINT_NULL
				fi
			fi

			if [ "$rootfsChksum" != "" ]; then
				echo "rootfs-$ROOTFS_IMAGE checksum: $rootfsChksum" > /dev/console
				$SETENV rootfsChecksum$ROOTFS_IMAGE "$rootfsChksum" > $PRINT_NULL
			fi
			if [ "$SUPPORT_DTB" != "" ]; then
				if [ "$dtbChksum" != "" ]; then
					echo "dtb-$ROOTFS_IMAGE checksum: $dtbChksum" > /dev/console
					$SETENV dtbChecksum$DTB_IMAGE "$dtbChksum" > $PRINT_NULL
				fi
			fi
#			confChksum=`cat $HDR_INFO | grep $EXTFS_CHKSUM | cut -d ' ' -f 2`
#			if [ "$confChksum" != "" ]; then
#				echo "rootfs-etc-$NEW_IMAGE checksum: $confChksum"
#				$SETENV confChecksum$NEW_IMAGE "$confChksum" > $PRINT_NULL
#			fi
			if [ -z "$MTD_BOOTEXT" ]; then 
				echo "TLV_Write: MTD_BOOTEXT is empty" > /dev/console
			else
				bootextChksum=`cat $HDR_INFO | grep $BOOTEXT_CHKSUM | cut -d ' ' -f 2`
				if [ "$bootextChksum" != "" ]; then
					echo "bootext-$BOOTEXT_IMAGE checksum: $bootextChksum" > /dev/console
					$SETENV bootextChecksum$BOOTEXT_IMAGE "$bootextChksum" > $PRINT_NULL
				fi
				bootextLen=`cat $HDR_INFO | grep $BOOTEXT_LEN | cut -d ' ' -f 2`
				if [ "$bootextLen" != "" ]; then
					echo "bootext-$BOOTEXT_IMAGE Len: $bootextLen" > /dev/console
					$SETENV bootextLen$BOOTEXT_IMAGE "0x$bootextLen" > $PRINT_NULL
				fi
			fi
			zbootChksum=`cat $HDR_INFO | grep $ZBOOT_CHKSUM | cut -d ' ' -f 2`
			if [ "$zbootChksum" != "" ]; then
				echo "zboot-$ZBOOT_IMAGE checksum: $zbootChksum" > /dev/console
				$SETENV zbootChecksum$ZBOOT_IMAGE "$zbootChksum" > $PRINT_NULL
			fi
			defconfigChksum=`cat $HDR_INFO | grep $DEFCONFIG_CHKSUM | cut -d ' ' -f 2`
			if [ "$defconfigChksum" != "" ]; then
				echo "defconfig-$DEFCONFIG_IMAGE checksum: $defconfigChksum"  > /dev/console
				$SETENV defconfigChecksum$DEFCONFIG_IMAGE "$defconfigChksum" > $PRINT_NULL
			fi
#			rasChksum=`cat $HDR_INFO | grep $RAS_CHKSUM | cut -d ' ' -f 2`
#			if [ "$rasChksum" != "" ]; then
#				echo "ras-$RAS_IMAGE checksum: $rasChksum" > /dev/console
#				$SETENV rasChecksum$RAS_IMAGE "$rasChksum" > $PRINT_NULL
#			fi
			####### Update Checksum information
			if [ "$kernelLen" != "" ]; then
				echo "kernel-$KERNEL_IMAGE Len: $kernelLen" > /dev/console
				$SETENV kernelLen$KERNEL_IMAGE "0x$kernelLen" > $PRINT_NULL
			fi
			if [ "$rootfsLen" != "" ]; then
				echo "rootfs-$ROOTFS_IMAGE Len: $rootfsLen" > /dev/console
				$SETENV rootfsLen$ROOTFS_IMAGE "0x$rootfsLen" > $PRINT_NULL
			fi
			if [ "$SUPPORT_DTB" != "" ]; then
				if [ "$dtbLen" != "" ]; then
					echo "dtb-$DTB_IMAGE Len: $dtbLen" > /dev/console
					$SETENV dtbLen$DTB_IMAGE "0x$dtbLen" > $PRINT_NULL
				fi
			fi
#			confLen=`cat $HDR_INFO | grep $EXTFS_LEN | cut -d ' ' -f 2`
#			if [ "$confLen" != "" ]; then
#				echo "rootfs-etc-$NEW_IMAGE Len: $confLen"
#				$SETENV confLen$NEW_IMAGE "$confLen" > $PRINT_NULL
#			fi
			zbootLen=`cat $HDR_INFO | grep $ZBOOT_LEN | cut -d ' ' -f 2`
			if [ "$zbootLen" != "" ]; then
				echo "zboot-$ZBOOT_IMAGE Len: $zbootLen" > /dev/console
				$SETENV zbootLen$ZBOOT_IMAGE "0x$zbootLen" > $PRINT_NULL
			fi
#			defconfigLen=`cat $HDR_INFO | grep $DEFCONFIG_LEN | cut -d ' ' -f 2`
#			if [ "$defconfigLen" != "" ]; then
#				echo "defconfig-$DEFCONFIG_IMAGE Len: $defconfigLen"
#				$SETENV defconfigLen$DEFCONFIG_IMAGE "$defconfigLen" > $PRINT_NULL
#			fi
#			rasLen=`cat $HDR_INFO | grep $RAS_LEN | cut -d ' ' -f 2`
#			if [ "$rasLen" != "" ]; then
#				echo "ras-$RAS_IMAGE Len: $rasLen" > /dev/console
#				$SETENV rasLen$RAS_IMAGE "0x$rasLen" > $PRINT_NULL
#			fi

			####### Update newestImage, isVerify
			kernelVer=`cat $HDR_INFO | grep $KERNEL_VER | cut -d ' ' -f 2`
			if [ "$kernelVer" != "" ]; then
				echo "isVerify-$KERNEL_IMAGE: 0" > /dev/console
				$SETENV isVerify$KERNEL_IMAGE "0" > $PRINT_NULL
				echo "newestImage: $KERNEL_IMAGE" > /dev/console
				$SETENV newestImage $KERNEL_IMAGE > $PRINT_NULL
			fi

			####### Update restoreFlag
			if [ "$isRestoreEnv" = "1" ]; then
				echo "$RESTORE_FLAG: 1" > /dev/console
				$SETENV $RESTORE_FLAG 1 > $PRINT_NULL
			fi

			####### Disable TLVSaveLock and update TLV to flash
			$SETENV TLVSaveLock 0

		;;
	"update_TLV_noCommit")
			###update_TLV_noCommit" copy from update_TLV
			###It just remove commit step for OMCI SW download.
			
			### Get the new image partition 
			#$CFG_UTIL -m $CFG_DEV -r
			ACTIVE_IMAGE=`$PRINTENV newestImage`

			UBOOT_IMAGE=$((!$ACTIVE_IMAGE))
			BOOTEXT_IMAGE=$((!$ACTIVE_IMAGE))
			ZBOOT_IMAGE=$((!$ACTIVE_IMAGE))
			KERNEL_IMAGE=$((!$ACTIVE_IMAGE))
			ROOTFS_IMAGE=$((!$ACTIVE_IMAGE))
			DTB_IMAGE=$((!$ACTIVE_IMAGE))
			DEFCONFIG_IMAGE=$((!$ACTIVE_IMAGE))
#			RAS_IMAGE=$((!$ACTIVE_IMAGE))

			MTD_UBOOT=`cat /proc/mtd | grep uboot$UBOOT_IMAGE | cut -d ':' -f 1`
			MTD_BOOTEXT=`cat /proc/mtd | grep bootext$BOOTEXT_IMAGE | cut -d ':' -f 1`
			
			echo "Update TLV  no commit" > /dev/console

#			kernelVer=`cat $HDR_INFO | grep $KERNEL_VER | cut -d ' ' -f 2`
#			if [ "$kernelVer" != "" ]; then
#				echo "Upload Image as $KERNEL_IMAGE image"
#				$SETENV newestImage $KERNEL_IMAGE > $PRINT_NULL
#				# Set this image to be non-verify image
#				$SETENV isVerify$KERNEL_IMAGE 0 > $PRINT_NULL
#			fi

			####### Update Version information first
			kernelVer=`cat $HDR_INFO | grep $KERNEL_VER | cut -d ' ' -f 2`
			#kernelVer, rootfsVer, ubootVer, zbootVer is the same version
			if [ "$kernelVer" != "" ]; then
				echo "version-$KERNEL_IMAGE version: $kernelVer" > /dev/console
				$SETENV  version$KERNEL_IMAGE "$kernelVer" > $PRINT_NULL
			fi
#			rootfsVer=`cat $HDR_INFO | grep $ROOTFS_VER | cut -d ' ' -f 2`
#			if [ "$rootfsVer" != "" ]; then
#				echo "rootfs-$ROOTFS_IMAGE version: $rootfsVer"
#				$SETENV rootfsVer$ROOTFS_IMAGE "$rootfsVer" > $PRINT_NULL
#			fi
#			confVer=`cat $HDR_INFO | grep $EXTFS_VER | cut -d ' ' -f 2`
#			if [ "$confVer" != "" ]; then
#				echo "rootfs-etc-$NEW_IMAGE version: $confVer"
#				$SETENV confVer$NEW_IMAGE "$confVer" > $PRINT_NULL
#			fi
#			bootextVer=`cat $HDR_INFO | grep $BOOTEXT_VER | cut -d ' ' -f 2`
#			if [ "$bootextVer" != "" ]; then
#				echo "bootext-$BOOTEXT_IMAGE version: $bootextVer"
#				$SETENV bootextVer$BOOTEXT_IMAGE "$bootextVer" > $PRINT_NULL
#			else
#				TMP_BOOTEXT_IMAGE=$((!$BOOTEXT_IMAGE))
#				echo "bootext-$TMP_BOOTEXT_IMAGE version: $kernelVer"
#				$SETENV bootextVer$TMP_BOOTEXT_IMAGE "$kernelVer" > $PRINT_NULL
#			fi
#			zbootVer=`cat $HDR_INFO | grep $ZBOOT_VER | cut -d ' ' -f 2`
#			if [ "$zbootVer" != "" ]; then
#				echo "zboot-$ZBOOT_IMAGE version: $zbootVer"
#				$SETENV zbootVer$ZBOOT_IMAGE "$zbootVer" > $PRINT_NULL
#			else
#				TMP_ZBOOT_IMAGE=$((!$ZBOOT_IMAGE))
#				echo "zboot-$TMP_ZBOOT_IMAGE version: $kernelVer"
#				$SETENV zbootVer$TMP_ZBOOT_IMAGE "$kernelVer" > $PRINT_NULL
#			fi
#			defconfigVer=`cat $HDR_INFO | grep $DEFCONFIG_VER | cut -d ' ' -f 2`
#			if [ "$defconfigVer" != "" ]; then
#				echo "defconfig-$DEFCONFIG_IMAGE version: $defconfigVer"
#				$SETENV  defconfigVer$DEFCONFIG_IMAGE "$defconfigVer" > $PRINT_NULL
#			fi
			fw_version=`cat $HDR_INFO | grep $FW_VERSION | cut -d ' ' -f 2 | awk 'NR==1'`
			if [ "$fw_version" != "" ]; then
			#	echo "fw_version-$KERNEL_IMAGE version: $fw_version" > /dev/console
				$SETENV  fw_version$KERNEL_IMAGE "$fw_version" > $PRINT_NULL
			fi
			####### Update Checksum information
			kernelChksum=`cat $HDR_INFO | grep $KERNEL_CHKSUM | cut -d ' ' -f 2`
			if [ "$kernelChksum" != "" ]; then
				echo "kernel-$KERNEL_IMAGE checksum: $kernelChksum" > /dev/console
				$SETENV kernelChecksum$KERNEL_IMAGE "$kernelChksum" > $PRINT_NULL
			fi
			if [ -z "$MTD_UBOOT" ]; then 
				echo "TLV_Write: MTD_UBOOT is empty" > /dev/console
			else
				ubootChksum=`cat $HDR_INFO | grep $UBOOT_CHKSUM | cut -d ' ' -f 2`
				if [ "$ubootChksum" != "" ]; then
					echo "uboot-$UBOOT_IMAGE checksum: $ubootChksum" > /dev/console
					$SETENV ubootChecksum$UBOOT_IMAGE "$ubootChksum" > $PRINT_NULL
				fi
				ubootLen=`cat $HDR_INFO | grep $UBOOT_LEN | cut -d ' ' -f 2`
				if [ "$ubootLen" != "" ]; then
					echo "uboot-$UBOOT_IMAGE Len: $ubootLen" > /dev/console
					$SETENV ubootLen$UBOOT_IMAGE "0x$ubootLen" > $PRINT_NULL
				fi
			fi
			rootfsChksum=`cat $HDR_INFO | grep $ROOTFS_CHKSUM | cut -d ' ' -f 2`
			if [ "$rootfsChksum" != "" ]; then
				echo "rootfs-$ROOTFS_IMAGE checksum: $rootfsChksum" > /dev/console
				$SETENV rootfsChecksum$ROOTFS_IMAGE "$rootfsChksum" > $PRINT_NULL
			fi
			
			if [ "$SUPPORT_DTB" != "" ]; then
				dtbChksum=`cat $HDR_INFO | grep $DTB_CHKSUM | cut -d ' ' -f 2`
				if [ "$dtbChksum" != "" ]; then
					echo "dtb-$DTB_IMAGE checksum: $dtbChksum" > /dev/console
					$SETENV dtbChecksum$DTB_IMAGE "$dtbChksum" > $PRINT_NULL
				fi
			fi
#			confChksum=`cat $HDR_INFO | grep $EXTFS_CHKSUM | cut -d ' ' -f 2`
#			if [ "$confChksum" != "" ]; then
#				echo "rootfs-etc-$NEW_IMAGE checksum: $confChksum"
#				$SETENV confChecksum$NEW_IMAGE "$confChksum" > $PRINT_NULL
#			fi
			if [ -z "$MTD_BOOTEXT" ]; then 
				echo "TLV_Write: MTD_BOOTEXT is empty" > /dev/console
			else
				bootextChksum=`cat $HDR_INFO | grep $BOOTEXT_CHKSUM | cut -d ' ' -f 2`
				if [ "$bootextChksum" != "" ]; then
					echo "bootext-$BOOTEXT_IMAGE checksum: $bootextChksum" > /dev/console
					$SETENV bootextChecksum$BOOTEXT_IMAGE "$bootextChksum" > $PRINT_NULL
				fi
				bootextLen=`cat $HDR_INFO | grep $BOOTEXT_LEN | cut -d ' ' -f 2`
				if [ "$bootextLen" != "" ]; then
					echo "bootext-$BOOTEXT_IMAGE Len: $bootextLen" > /dev/console
					$SETENV bootextLen$BOOTEXT_IMAGE "0x$bootextLen" > $PRINT_NULL
				fi
			fi
			zbootChksum=`cat $HDR_INFO | grep $ZBOOT_CHKSUM | cut -d ' ' -f 2`
			if [ "$zbootChksum" != "" ]; then
				echo "zboot-$ZBOOT_IMAGE checksum: $zbootChksum" > /dev/console
				$SETENV zbootChecksum$ZBOOT_IMAGE "$zbootChksum" > $PRINT_NULL
			fi
			defconfigChksum=`cat $HDR_INFO | grep $DEFCONFIG_CHKSUM | cut -d ' ' -f 2`
			if [ "$defconfigChksum" != "" ]; then
				echo "defconfig-$DEFCONFIG_IMAGE checksum: $defconfigChksum"  > /dev/console
				$SETENV defconfigChecksum$DEFCONFIG_IMAGE "$defconfigChksum" > $PRINT_NULL
			fi
#			rasChksum=`cat $HDR_INFO | grep $RAS_CHKSUM | cut -d ' ' -f 2`
#			if [ "$rasChksum" != "" ]; then
#				echo "ras-$RAS_IMAGE checksum: $rasChksum" > /dev/console
#				$SETENV rasChecksum$RAS_IMAGE "$rasChksum" > $PRINT_NULL
#			fi
			####### Update Checksum information
			kernelLen=`cat $HDR_INFO | grep $KERNEL_LEN | cut -d ' ' -f 2`
			if [ "$kernelLen" != "" ]; then
				echo "kernel-$KERNEL_IMAGE Len: $kernelLen" > /dev/console
				$SETENV kernelLen$KERNEL_IMAGE "0x$kernelLen" > $PRINT_NULL
			fi
			rootfsLen=`cat $HDR_INFO | grep $ROOTFS_LEN | cut -d ' ' -f 2`
			if [ "$rootfsLen" != "" ]; then
				echo "rootfs-$ROOTFS_IMAGE Len: $rootfsLen" > /dev/console
				$SETENV rootfsLen$ROOTFS_IMAGE "0x$rootfsLen" > $PRINT_NULL
			fi
			
			if [ "$SUPPORT_DTB" != "" ]; then
				dtbLen=`cat $HDR_INFO | grep $DTB_LEN | cut -d ' ' -f 2`
				if [ "$dtbLen" != "" ]; then
					echo "dtb-$DTB_IMAGE Len: $dtbLen" > /dev/console
					$SETENV dtbLen$DTB_IMAGE "0x$dtbLen" > $PRINT_NULL
				fi
			fi
#			confLen=`cat $HDR_INFO | grep $EXTFS_LEN | cut -d ' ' -f 2`
#			if [ "$confLen" != "" ]; then
#				echo "rootfs-etc-$NEW_IMAGE Len: $confLen"
#				$SETENV confLen$NEW_IMAGE "$confLen" > $PRINT_NULL
#			fi
			zbootLen=`cat $HDR_INFO | grep $ZBOOT_LEN | cut -d ' ' -f 2`
			if [ "$zbootLen" != "" ]; then
				echo "zboot-$ZBOOT_IMAGE Len: $zbootLen" > /dev/console
				$SETENV zbootLen$ZBOOT_IMAGE "0x$zbootLen" > $PRINT_NULL
			fi
#			defconfigLen=`cat $HDR_INFO | grep $DEFCONFIG_LEN | cut -d ' ' -f 2`
#			if [ "$defconfigLen" != "" ]; then
#				echo "defconfig-$DEFCONFIG_IMAGE Len: $defconfigLen"
#				$SETENV defconfigLen$DEFCONFIG_IMAGE "$defconfigLen" > $PRINT_NULL
#			fi
#			rasLen=`cat $HDR_INFO | grep $RAS_LEN | cut -d ' ' -f 2`
#			if [ "$rasLen" != "" ]; then
#				echo "ras-$RAS_IMAGE Len: $rasLen" > /dev/console
#				$SETENV rasLen$RAS_IMAGE "0x$rasLen" > $PRINT_NULL
#			fi

			####### Update newestImage, isVerify
			kernelVer=`cat $HDR_INFO | grep $KERNEL_VER | cut -d ' ' -f 2`
			NEWEST_IMAGE_VERSION=`$PRINTENV newestImage`
			if [ "$kernelVer" != "" ]; then
				echo "isVerify-$KERNEL_IMAGE: 0" > /dev/console
				$SETENV isVerify$KERNEL_IMAGE "0" > $PRINT_NULL
				echo "newestImage:  $NEWEST_IMAGE_VERSION" > /dev/console
			fi

			####### Update restoreFlag
			if [ "$isRestoreEnv" = "1" ]; then
				echo "$RESTORE_FLAG: 1" > /dev/console
				$SETENV $RESTORE_FLAG 1 > $PRINT_NULL
			fi
		;;
	"write_flash")
		# 1. Check which image we are going to burn
		echo "write_flash" > /dev/console
		#$CFG_UTIL -m $CFG_DEV -r
		ACTIVE_IMAGE=`$PRINTENV newestImage`

		UBOOT_IMAGE=$((!$ACTIVE_IMAGE))
		BOOTEXT_IMAGE=$((!$ACTIVE_IMAGE))
		ZBOOT_IMAGE=$((!$ACTIVE_IMAGE))
		KERNEL_IMAGE=$((!$ACTIVE_IMAGE))
		ROOTFS_IMAGE=$((!$ACTIVE_IMAGE))
		DEFCONFIG_IMAGE=$((!$ACTIVE_IMAGE))
		DTB_IMAGE=$((!$ACTIVE_IMAGE))
#		RAS_IMAGE=$((!$ACTIVE_IMAGE))

		if [ "$2" == "" ];then
			NEW_IMAGE=$KERNEL_IMAGE;
		else
			NEW_IMAGE=$2;
			KERNEL_IMAGE=$2
			ROOTFS_IMAGE=$2
			DEFCONFIG_IMAGE=$2
			DTB_IMAGE=$2
#			RAS_IMAGE=$2
			
		fi
		echo "uboot=$UBOOT_IMAGE, bootext=$BOOTEXT_IMAGE zboot=$ZBOOT_IMAGE"
		if [ "$SUPPORT_DTB" != "" ]; then
			echo "kernel=$KERNEL_IMAGE, rootfs=$ROOTFS_IMAGE, defconfig=$DEFCONFIG_IMAGE, dtb=$DTB_IMAGE"
		else
		echo "kernel=$KERNEL_IMAGE, rootfs=$ROOTFS_IMAGE, defconfig=$DEFCONFIG_IMAGE"
		fi
#		echo "ras=$RAS_IMAGE"
		# 2. Get MTD partition information
		MTD_KERNEL=`cat /proc/mtd  | grep linux$KERNEL_IMAGE | cut -d ':' -f 1`
		MTD_ROOTFS=`cat /proc/mtd  | grep rootfs$ROOTFS_IMAGE | cut -d ':' -f 1`
		MTD_DTB=`cat /proc/mtd  | grep dtb$DTB_IMAGE | cut -d ':' -f 1`
		#MTD_ROOTFS_ETC=`cat /proc/mtd  | grep RootFS-etc-$NEW_IMAGE | cut -d ':' -f 1`
		MTD_UBOOT=`cat /proc/mtd | grep uboot$UBOOT_IMAGE | cut -d ':' -f 1`
		MTD_BOOTEXT=`cat /proc/mtd | grep bootext$BOOTEXT_IMAGE | cut -d ':' -f 1`
		MTD_ZBOOT=`cat /proc/mtd | grep zboot$ZBOOT_IMAGE | cut -d ':' -f 1`
		#MTD_STARTER=`cat /proc/mtd | grep -w boot | cut -d ':' -f 1`
		MTD_DEFCONFIG=`cat /proc/mtd  | grep defconfig$DEFCONFIG_IMAGE | cut -d ':' -f 1`
		MTD_USERCONFIG=`cat /proc/mtd  | grep userconfig | cut -d ':' -f 1`
#		MTD_RAS=`cat /proc/mtd  | grep ras$RAS_IMAGE | cut -d ':' -f 1`
		#echo $MTD_KERNEL
		#echo $MTD_ROOTFS
		#echo $MTD_ROOTFS_ETC

		# Program flash for bootext		
		writeBootext $BOOTEXT_FILE
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $BOOTEXT_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
#			/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
#			/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $BOOTEXT_FILE
			return 1
		fi
		if [ -f $BOOTEXT_FILE ]; then
			#ACTIVE_IMAGE=$(($ACTIVE_IMAGE^8))
			echo "bootext=$BOOTEXT_IMAGE written" > /dev/console
			rm -f $BOOTEXT_FILE
			isRestoreEnv=1
		fi

		# Program flash for default configuration
		writeDefconfig $DEFCONFIG_FILE
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $DEFCONFIG_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $DEFCONFIG_FILE
			return 1
		fi
		if [ -f $DEFCONFIG_FILE ]; then
			#ACTIVE_IMAGE=$(($ACTIVE_IMAGE^4))
			echo "defconfig=$DEFCONFIG_IMAGE written" > /dev/console
			rm -f $DEFCONFIG_FILE
		fi

		# Program flash for user configuration
		writeUserconfig $USERCONFIG_FILE  
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $USERCONFIG_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $USERCONFIG_FILE
			return 1
		fi
		if [ -f $USERCONFIG_FILE ]; then
			echo "userconfig=$USERCONFIG_FILE written" > /dev/console
			rm -f $USERCONFIG_FILE
		fi

		# Program flash for uboot		
		writeUboot $UBOOT_FILE
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $UBOOT_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $UBOOT_FILE
			return 1
		fi
		if [ -f $UBOOT_FILE ]; then
			echo "uboot=$UBOOT_IMAGE written" > /dev/console
			rm -f $UBOOT_FILE
			isRestoreEnv=1
		fi

		# Program flash for zboot		
		writeZboot $ZBOOT_FILE
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $ZBOOT_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $ZBOOT_FILE
			return 1
		fi
		if [ -f $ZBOOT_FILE ]; then
			#ACTIVE_IMAGE=$(($ACTIVE_IMAGE^16))
			echo "zboot=$ZBOOT_IMAGE written" > /dev/console
			rm -f $ZBOOT_FILE
			isRestoreEnv=1
		fi

		# Program flash for starter
#		writeBoot $STARTER_FILE
#		if [ $FLASHWRITE_CHKOK != "1" ]; then
#			echo "Write $STARTER_FILE failed!!!" > /dev/console
#			# enable H/W monitor watchdog
#			/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
#			/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
#			rm -f $STARTER_FILE
#			$RM -f $TMP_STARTER_MRD_FILE
#			return 1
#		fi
#		if [ -f $STARTER_FILE ]; then
#			echo "starter=$STARTER_FILE written" > /dev/console
#			rm -f $STARTER_FILE
#			$RM -f $TMP_STARTER_MRD_FILE
#		fi

		# Program flash for kernel
		writeKernel $KERNEL_FILE
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $KERNEL_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $KERNEL_FILE
			return 1
		fi
		if [ -f $KERNEL_FILE ]; then
			#ACTIVE_IMAGE=$(($ACTIVE_IMAGE^1))
			echo "kernel=$KERNEL_IMAGE written" > /dev/console
			rm -f $KERNEL_FILE
		fi
	
		# Program flash for /etc 
		#writeExtfs $ETCFS_FILE

		# Program flash for root file system
		writeRootfs $ROOTFS_FILE
		if [ $FLASHWRITE_CHKOK != "1" ]; then
			echo "Write $ROOTFS_FILE failed!!!" > /dev/console
			# enable H/W monitor watchdog
			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
			rm -f $ROOTFS_FILE
			return 1
		fi
		if [ -f $ROOTFS_FILE ]; then
			#ACTIVE_IMAGE=$(($ACTIVE_IMAGE^2))
			echo "rootfs=$ROOTFS_IMAGE written" > /dev/console
			rm -f $ROOTFS_FILE
		fi
		
		if [ "$SUPPORT_DTB" != "" ]; then
			# Program flash for DTB partition
			writeDTB $DTB_FILE
			if [ $FLASHWRITE_CHKOK != "1" ]; then
				echo "Write $DTB_FILE failed!!!" > /dev/console
				rm -f $DTB_FILE
				return 1
			fi
			if [ -f $DTB_FILE ]; then
				echo "dtb=$DTB_IMAGE written" > /dev/console
				rm -f $DTB_FILE
			fi
		fi
		
		# Program flash for ras file system
#		writeRas $RAS_FILE
#		if [ $FLASHWRITE_CHKOK != "1" ]; then
#			echo "Write $RAS_FILE failed!!!" > /dev/console
#			# enable H/W monitor watchdog
#			#/sbin/set_hw_monitor_watchdog_mode unlock > /dev/console
#			#/sbin/set_hw_monitor_watchdog_mode strobe  > /dev/console
#			rm -f $RAS_FILE
#			return 1
#		fi
#		if [ -f $RAS_FILE ]; then
#			#ACTIVE_IMAGE=$(($ACTIVE_IMAGE^2))
#			echo "Ras=$RAS_IMAGE written" > /dev/console
#			rm -f $RAS_FILE
#		fi

		echo "ACTIVE_IMAGE = $((!$ACTIVE_IMAGE))" > /dev/console

		# Set CFG active partition to the newest one
		#$CFG_UTIL -m $CFG_DEV -w -a $ACTIVE_IMAGE
		#$SETENV bootImage $ACTIVE_IMAGE > $PRINT_NULL
		return 0
		;;
	"reboot")
		reboot
		;;
	*)
		echo "Unkwnon command, should be extract | check | write_flash | update_TLV | update_TLV_noCommit | reboot " > /dev/console
		;;
esac
exit 0

