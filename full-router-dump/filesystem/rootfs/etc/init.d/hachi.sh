#!/bin/sh

sys atmc
if [ -e /tmp/teConfigFlag ]; then
        teConfigFlag=`cat /tmp/teConfigFlag`
        if [ $teConfigFlag != 1 ]; then
                if [ -e /usr/bin/hachi ] ; then
                        /usr/bin/hachi &
                fi
        fi
fi
