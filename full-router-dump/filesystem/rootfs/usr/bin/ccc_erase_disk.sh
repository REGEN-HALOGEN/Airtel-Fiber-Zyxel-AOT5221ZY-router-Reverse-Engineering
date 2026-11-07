#!/bin/sh

#cat /proc/mtd
#dev:    size   erasesize  name
#mtd0: 007c0000 00010000 "rootfs,kernel"
#mtd1: 00020000 00010000 "mrd_cert"
#mtd2: 03e00000 00004000 "storage"
#mtd3: 00200000 00004000 "config"

# erase MRD_Cert partition
# flash_eraseall /dev/mtd1

# Certificate : 0x40 ~ 0x4D
if [ -e /etc/MLD_Config.sh ]; then
	. /etc/MLD_Config.sh
fi


DELETE_INDEX=""
for X in $(seq 64 77)
do
        INDEX=`printf "%x" $X`
        DELETE_INDEX="$DELETE_INDEX $INDEX"
done
mcputil del $DELETE_INDEX

# erase MRD cert A0
MRD_DUMP_FILE="/etc/zyfwupgrade"
ProductName=$(awk "\$1==\"ProductName\" {print \$2}" $MRD_DUMP_FILE)
if [ $ProductName == "P-2812HNU-F1" ] || [ $ProductName == "P-2812HNUL-F1" ]; then # Support software wan mode switch via configuration instead of  hareware switch button.
        mcputil del A0
fi

# erase Config partition
# flash_eraseall /dev/mtd3
rm -rf /mnt/Config/*

# remove 69 files
rm -rf /app/ztr69_*
rm -rf /app/cert

#remove PPPoE files
rm -rf /app/ppp/*

#remove OpenVPN file
if [ -d /app/OpenVPN ]; then
	rm -rf /app/OpenVPN
fi

#remove dog hachi file
if [ -d /app/dogHachi ]; then
	rm -rf /app/dogHachi
fi

if [ "$MLD_PLATFORM_CORTINA" == "MLD_PLATFORM_CORTINA" ]; then
	rm -f /config/nonvolatile/scfg.txt #Remove platform scfg.txt
	cp -af /etc/scfg/scfg.txt.customized /config/nonvolatile/scfg.txt
fi

exit 0
