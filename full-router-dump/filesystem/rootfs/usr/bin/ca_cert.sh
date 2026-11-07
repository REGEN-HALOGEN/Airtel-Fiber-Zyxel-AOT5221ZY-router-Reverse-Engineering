#!/bin/sh
#==========================
# PARAMETER DEFINE
#==========================
CALISTPATH="/tmp/ca_cert.list"


#==========================
# FUNCTION LIST
#==========================
printInfo ()
{
	echo "sh $PROGRAMNAME upload   <StartIndex(dec)> <MaxNumber(dec)> <CertFullPath> <AssembleFullPath> <ListFileFullPath>"
	echo "sh $PROGRAMNAME download <StartIndex(dec)> <MaxNumber(dec)> <CertFullPath> <AssembleFullPath>"
	exit 1
}

assembleCert()
{
	cd $CERTPATH

	rm $ASSEMBLEPATH

	LISTNAME=`ls $CertFullPath`
	if [ "$LISTNAME" != "" ] ; then 
		for FILENAME in $LISTNAME
		do
			cat $FILENAME >> $ASSEMBLEPATH
			echo >> $ASSEMBLEPATH
		done
	fi
}

uploadCertCheck ()
{
	if [ $ARGC -lt 6 ] ; then
		printInfo;
	elif [ ! -e $LISTFILE ] ; then
		echo "$LISTFILE not exist"
		exit 1;
	fi
}

uploadCert ()
{
	uploadCertCheck;

	MODIFY_CMD=""
	DELETE_CMD=""
	INDEX=`printf "%x" $STARTINDEX`

	SIZE=`cat $LISTFILE | wc -c`

	if [ $SIZE -ne 0 ] ; then
		# create upload certificate list file string
		MODIFY_CMD="$MODIFY_CMD $INDEX $LISTFILE "

		let STARTINDEX=STARTINDEX+1

		# get certificate list array
		LISTNAME=`cat $LISTFILE`

		# create upload certificate file string
		LOOP=1

		for FILENAME in $LISTNAME
		do
			if [ $LOOP -gt  $MAXNUMBER ] ; then
				break
			fi
			INDEX=`printf "%x" $STARTINDEX`
			MODIFY_CMD="$MODIFY_CMD $INDEX $CERTPATH/$FILENAME "
			let STARTINDEX=STARTINDEX+1
			let LOOP=LOOP+1
		done
	else
		# create remove certificate list file string
		DELETE_CMD="$DELETE_CMD $INDEX "

		let STARTINDEX=STARTINDEX+1
		LOOP=1
	fi

	# create remove unused certificate file string
	while [ $LOOP -le $MAXNUMBER ]
	do
		INDEX=`printf "%x" $STARTINDEX`
		DELETE_CMD="$DELETE_CMD $INDEX "
		let STARTINDEX=STARTINDEX+1
		let LOOP=LOOP+1
	done

	# do modify certificate file
	if [ "$MODIFY_CMD" != "" ] ; then 
		echo "mcputil modify $MODIFY_CMD"
		mcputil modify $MODIFY_CMD
	fi

	# do remove certificate file
	if [ "$DELETE_CMD" != "" ] ; then 
		echo "mcputil del $DELETE_CMD"
		mcputil del $DELETE_CMD
	fi

	# remove certificate list file
	rm $LISTFILE

	echo "finish upload certificate"
}

downloadCertCheck ()
{
	if [ $ARGC -lt 5 ] ; then
		printInfo;
	elif [ ! -e $CERTPATH ] ; then
		echo "mkdir -p $CERTPATH"
	fi
}

downloadCert ()
{
	downloadCertCheck;

	# download certificate list file
	INDEX=`printf "%x" $STARTINDEX`
	mcputil read $INDEX $CALISTPATH

	if [ -e $CALISTPATH ] ; then
		# get certificate list array
		LISTNAME=`cat $CALISTPATH`

		# create download certificate file string
		let STARTINDEX=STARTINDEX+1
		LOOP=1
		READ_CMD=""
		for FILENAME in $LISTNAME
		do
			if [ $LOOP -gt $MAXNUMBER ] ; then
				break;
			fi
			INDEX=`printf "%x" $STARTINDEX`
			READ_CMD="$READ_CMD $INDEX $CERTPATH/$FILENAME "
			let STARTINDEX=STARTINDEX+1
			let LOOP=LOOP+1
		done

		# do download certificate file
		if [ "$READ_CMD" != "" ] ; then 
			echo "mcputil read $READ_CMD"
			mcputil read $READ_CMD
		fi

		# remove certificate list file
		rm $CALISTPATH
	fi

	echo "finish download certificate"
}


#============================
# main function
#============================
ARGC=$#
PROGRAMNAME=$0
ACTION=$1
STARTINDEX=$2
MAXNUMBER=$3
CERTPATH=$4
ASSEMBLEPATH=$5
LISTFILE=$6

case $ACTION in
	"upload")
		uploadCert;
		assembleCert;
		;;
	"download")
		downloadCert;
		assembleCert;
		;;
	*)
		printInfo;
		;;
esac
exit 0

