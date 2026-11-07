#!/bin/sh
if [ -e /app/cert ]; then
	echo "Skip copy CA to target folder." > /dev/console
else
	sys atcc | awk '{print $5}' > /tmp/currCountry
	if [ -e /tmp/currCountry ]; then
		/bin/mkdir -m 0777 -p /var/cert/ca
		currCountry=`cat /tmp/currCountry`
		case ${currCountry} in
		C5)
			cp -f  /usr/var/cert/CL/* /var/cert/ca/
			;;
		D0)
			cp -f  /usr/var/cert/BR/* /var/cert/ca/
			;;
		D5)
			cp -f  /usr/var/cert/ES/* /var/cert/ca/
			;;
		ED)
			cp -f /usr/var/cert/DE/* /var/cert/ca/
			;;
		*)
			echo "ERROR: Not support this country code ${currCountry}!" > /dev/console
			;;
		esac
	else
		echo "ERROR: Cannot get country code!" > /dev/console
	fi
fi
