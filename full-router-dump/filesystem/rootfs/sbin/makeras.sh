NPUT=$*

UTL_VER=0.0.1
METADATA=fw.txt
MAKE_ZLFW_HEADER=./make_zlfw_header_${UTL_VER}
APPEND_ZLFW_HEADER=./append_zlfw_header_${UTL_VER}
ROOTFS_DIR=$ROOTFS_INSTALL_PATH
BUILD_DIR=../../build
IMAGE_NAME=ras.bin

LINE_SEP="======================================================================================"

# Get uboot image names
FNAME=$(awk "\$1~/^EXT_IM_UBOOT/ {print \$3}" $METADATA)

if [ "$FNAME" != "NULL" ] && [ "$FNAME" != "null" ]; then
	echo "===== Start to generate bootbase image ====="
	echo "Step1: Parse config and generate bootbase zlfw header template"
	${MAKE_ZLFW_HEADER} -u -i ${METADATA}
	if [ $? -ne 0 ]; then
        	echo "Parsing configuration file failed"
        	exit 1
	fi
	echo "==== process $FNAME ===="
        FBASE=$(basename $FNAME)
        TYPE=$(awk "\$3==\"$FNAME\" {print \$1}" $METADATA)
        IM_TYPE=$(awk "\$1==\"EXT_IM_UBOOT\" {print \$4}" $METADATA)
	echo "${APPEND_ZLFW_HEADER} -t $IM_TYPE -f $TYPE -i $FNAME  -o ${FBASE}_zlh"
	BOOTBASE_CHECKSUM=`${APPEND_ZLFW_HEADER} -t $IM_TYPE -f $TYPE -i $FNAME  -o ${FBASE}_zlh`
        if [ $? -ne 0 ]; then
                echo "append zlfw header to $FNAME failed"
                exit 1
        fi
	mv ${FBASE}_zlh ${BUILD_DIR}/final_images
	rm header.bin        
	echo ""
fi

# Get image names
KERNEL=$(awk "\$1==\"KERNEL\" {print \$3}" $METADATA)
FLAG=$(awk "\$1==\"KERNEL\" {print \$2}" $METADATA)
if [ "$KERNEL" == "NULL" ] || [ "$KERNEL" == "null" ]; then
	KERNEL=""
fi

ROOTFS=$(awk "\$1==\"ROOTFS\" {print \$3}" $METADATA)
FLAG=$(awk "\$1==\"ROOTFS\" {print \$2}" $METADATA)
if [ "$ROOTFS" == "NULL" ] || [ "$ROOTFS" == "null" ]; then
	ROOTFS=""
fi

EXTFS=$(awk "\$1==\"EXTFS\" {print \$3}" $METADATA)
FLAG=$(awk "\$1==\"EXTFS\" {print \$2}" $METADATA)
if [ "$EXTFS" == "NULL" ] || [ "$EXTFS" == "null" ]; then
	EXTFS=""
fi

EXTIM=$(awk "\$1~/^EXT_IM_.*/ {print \$3}" $METADATA)

ROMFILE=$(awk "\$1==\"DEFAULT_ROMFILE\" {print \$3}" $METADATA)
if [ "$ROMFILE" == "NULL" ] || [ "$ROMFILE" == "null" ]; then
	$ROMFILE=""
fi


# Create build dir if needed
if [ ! -d $BUILD_DIR ]; then
	mkdir -p $BUILD_DIR
fi


# Read configuration file (fw.txt), and generate header.bin
echo "===== Start to generate final image: $BUILD_DIR/$IMAGE_NAME ====="
echo "$LINE_SEP"
echo "Step1: Parse config:"
${MAKE_ZLFW_HEADER} -i ${METADATA}
if [ $? -ne 0 ]; then
        echo "Parsing configuratio file failed"
        exit 1
fi

echo "$LINE_SEP"
echo "Step 2: Process each image file"

################################################################################
#	DCMA memo: This software is from CPE_SW1, however, it is not suitable
#	for GPON product, therefore, the $KERNEL, $ROOTFS, $EXTFS and $ROMFILE
#       is not used in GPON product. I will remove these section. If we need it 
#	in future, please merge it back from CPE_SW1 trunk 
################################################################################

LIST=

if [ -n "$KERNEL" ]; then
	echo "=== process kernel ==="
fi




# add firmware header to extfs, and update EXTFS_CHECKSUM in ${METADATA}
if [ -n "$EXTFS" ]; then
	echo "==== process extfs ===="
fi


# add firmware header to rootfs, Update ROOTFS_CHECKSUM in ${METADATA}
if [ -n "$ROOTFS" ]; then
	echo "==== process rootfs ===="
fi


# other images
for FNAME in $EXTIM
do
	FLAG=$(awk "\$3==\"$FNAME\" {print \$2}" $METADATA)
	if [ "$FNAME" != "NULL" ] && [ "$FNAME" != "null" ]; then
		echo "==== process $FNAME ===="
		FBASE=$(basename $FNAME)
		TYPE=$(awk "\$3==\"$FNAME\" {print \$1}" $METADATA)
		IM_TYPE=$(awk "\$1==\"$TYPE\" {print \$4}" $METADATA)
		${APPEND_ZLFW_HEADER} -t $IM_TYPE -f $TYPE -i $FNAME -o ${FBASE}_zlh
		if [ $? -ne 0 ]; then
			echo "append zl_firmware header to $FNAME failed"
			exit 1
		fi
		echo ""

		LIST=${LIST}" "${FBASE}_zlh
	fi
done


# Generate a final firmware image
echo "$LINE_SEP"
echo "Step 3: Cat all files to $BUILD_DIR/$IMAGE_NAME"
cat $LIST >> $BUILD_DIR/${IMAGE_NAME}
chmod 644 ${BUILD_DIR}/${IMAGE_NAME}

mkdir -p ${BUILD_DIR}/final_images
mv $LIST ${BUILD_DIR}/final_images
cp -f ${BUILD_DIR}/${IMAGE_NAME} ${BUILD_DIR}/final_images
echo "$LINE_SEP"
echo ""
echo "All necessary files are copied to directory '$BUILD_DIR/final_images' for release."
echo ""
echo "FIRMWARE ID -->" `grep "^VERSION" ${METADATA} | awk -F" " '{print $3}'`
if [ -n "$KERNEL" ]; then
	echo "Kernel Checksum -->" `grep "^KERNEL_CHECKSUM" ${METADATA} | awk -F" " '{print $3}'`
fi
if [ -n "$ROOTFS" ]; then
	echo "ROOTFS Checksum -->" `grep "^ROOTFS_CHECKSUM" ${METADATA} | awk -F" " '{print $3}'`
fi
if [ -n "$EXTFS" ]; then
	echo "EXTFS Checksum -->" `grep "^EXTFS_CHECKSUM" ${METADATA} | awk -F" " '{print $3}'`
fi
echo ""
echo "Final firmware image: $BUILD_DIR/$IMAGE_NAME"
