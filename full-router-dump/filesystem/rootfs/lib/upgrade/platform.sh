#!/bin/sh

tmp_dir="/tmp/fwu"
sentinel="fwu.sh"
sentinel_gz="fwu.sh.gz"
md5_cmp="md5.txt"
md5_cmd="md5sum"
md5_tmp="md5_tmp" 
md5_rt_result="md5_rt_result.txt"
diff_cmd="diff"

tar_img_idx="tar_img_idx"

# extra programs for temporary ramfs root
RAMFS_COPY_BIN="diff nv ubinfo"
RAMFS_COPY_DATA=
export RAMFS_COPY_BIN RAMFS_COPY_DATA

# Description:
#   call this function when file download finish.
# Return Value:
#   0: Success
#   1: Failure
platform_check_image() {
	case "$1" in
		/*)
			img="$1"
			;;
		*)
			img="`pwd`/$1"
			;;
	esac
	echo "img=$img"
	
	# Stop this script upon any error
	#set -e

	if [ -d $tmp_dir ]; then
		rm -rf $tmp_dir
	fi
	mkdir -p $tmp_dir

	cd $tmp_dir 
	tar -xf $img $sentinel $md5_cmp
	if [ $? != 0 ]; then
		tar -xf $img $sentinel_gz $md5_cmp
		if [ $? != 0 ]; then
			echo "Failed to extract $img, aborted image updating !"
			return 1
		else
			gzip -d $sentinel_gz
			if [ $? != 0 ]; then
				echo "$sentinel NOT found, aborted image updating !"
				return 1;
			fi
		fi
	fi

	grep $sentinel $md5_cmp > $md5_tmp
	$md5_cmd $sentinel > $md5_rt_result
	$diff_cmd $md5_rt_result $md5_tmp

	if [ $? != 0 ]; then 
	    echo "$sentinel md5_sum inconsistent, aborted image updating !"
	    return 1
	fi
}

# Before switch to ramfs
# Return Value:
#   0: Success
#   1: Failure
platform_pre_upgrade() {
	# For dual image, if active is '0' now, then '1' should be upgraded
	nv getenv sw_active | awk -F'=' '{x=1-$2}END{print x}' > $tmp_dir/$tar_img_idx
}

# Description:
#   Switch ramfs, and starting flash image
# Return Value:
#   0: Success
#   1: Failure
platform_do_upgrade() {
	partition=`cat $tmp_dir/$tar_img_idx`
	case "$1" in
		/*)
			img="$1"
			;;
		*)
			img="`pwd`/$1"
			;;
	esac
	echo "img=$img will flash to partition $partition."

	lowmem=0
#	if [ $# = 3 ]; then
#		lowmem=$3
#	fi

	# Run firmware upgrade script extracted from image tar ball
	sh $tmp_dir/$sentinel $partition $img $lowmem
	if [ $? != 0 ]; then
		echo "Incorrect image, aborted image updating !"
		return 1
	else
		nv setenv sw_updater web
		echo "set sw_updater to web."
		nv setenv sw_tryactive $partition
		echo "set tryactive to $partition."
	fi
}

# Return Value:
#	0: Success
#	1: Failure
platform_copy_config() {
	return 0
}

