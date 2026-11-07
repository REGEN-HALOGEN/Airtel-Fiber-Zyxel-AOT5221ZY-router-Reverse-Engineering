#!/bin/sh /etc/rc.common

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib/MSTC:/usr/lib/MSTC

MR_LogLevel=6
DNS_LogLevel=6
BE_LogLevel=6

SetLogLV_MR=/xdata/._CCC_LV_MR
SetLogLV_DNS=/xdata/._CCC_LV_DNS
SetLogLV_BE=/xdata/._CCC_LV_BE

if [ -f $SetLogLV_MR ]; then
        FindLogLV=`cat $SetLogLV_MR`
        if [ "$FindLogLV" = "0" ] || [ "$FindLogLV" = "1" ] || [ "$FindLogLV" = "2" ] \
                || [ "$FindLogLV" = "3" ] || [ "$FindLogLV" = "4" ] || [ "$FindLogLV" = "5" ] \
                || [ "$FindLogLV" = "6" ] || [ "$FindLogLV" = "7" ]; then

                MR_LogLevel=$FindLogLV
        fi
fi

if [ -f $SetLogLV_DNS ]; then
        FindLogLV=`cat $SetLogLV_DNS`
        if [ "$FindLogLV" = "0" ] || [ "$FindLogLV" = "1" ] || [ "$FindLogLV" = "2" ] \
                || [ "$FindLogLV" = "3" ] || [ "$FindLogLV" = "4" ] || [ "$FindLogLV" = "5" ] \
                || [ "$FindLogLV" = "6" ] || [ "$FindLogLV" = "7" ]; then

                DNS_LogLevel=$FindLogLV
        fi
fi

if [ -f $SetLogLV_BE ]; then
        FindLogLV=`cat $SetLogLV_BE`
        if [ "$FindLogLV" = "0" ] || [ "$FindLogLV" = "1" ] || [ "$FindLogLV" = "2" ] \
                || [ "$FindLogLV" = "3" ] || [ "$FindLogLV" = "4" ] || [ "$FindLogLV" = "5" ] \
                || [ "$FindLogLV" = "6" ] || [ "$FindLogLV" = "7" ]; then

                BE_LogLevel=$FindLogLV
        fi
fi


W_LOG()
{
        if [ $DEBUG -eq 1 ]; then
                echo "[${PNAME}] $@" > /dev/console
        fi
}

W_ERR()
{
        if [ $DEBUG -eq 1 ]; then
                echo "[${PNAME}][ERR] $@" > /dev/console
        fi
}


start()
{
                echo "CCCMR_LogLevel  = $MR_LogLevel " > /dev/console
                echo "CCCDNS_LogLevel = $DNS_LogLevel " > /dev/console
                echo "CCCBE_LogLevel  = $BE_LogLevel " > /dev/console

                echo "Starting MLD CCC(Common Configuration Center)..." >> /dev/console
                cp -rf /usr/var/* /var/
                /bin/mkdir -m 0777 -p /var/rdm
                /bin/mkdir -m 0777 -p /var/pdm
                ln -snf /var/default-rdm/config.rdm /var/rdm/config.rdm
                ln -snf /var/default-pdm/config.xml /var/pdm/config.default.xml
                ln -snf /var/pdm/config.xml /var/pdm/config.rom

                ##bring_up ccc##
                /usr/bin/ccc_mr -l $MR_LogLevel &
                /usr/bin/ccc_das -l $DNS_LogLevel &
                /usr/bin/ccc_be -l $BE_LogLevel&
}
