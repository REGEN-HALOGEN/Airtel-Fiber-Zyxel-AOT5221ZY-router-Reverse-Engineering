#!/bin/sh
#

echo "WiFi alloc_xmitframe_ext recovery detect start!!!" > /dev/console

DO_RECOVERY=1
cmd=$DO_RECOVERY

while true
do
	if [ -f /proc/net/rtk_wifi6/wlan0/stats ]; then
		recovery_detect=$(cat /proc/net/rtk_wifi6/wlan0/stats | tail -n 1 | cut -d : -f 2)
		if [ -n "$recovery_detect" ]; then
			if [ $recovery_detect = $cmd ]; then
				echo "wlan0 : recovery_detect is 1 !!!" > /dev/console
				echo 3 3 > /proc/net/rtk_wifi6/log_level
				cat /proc/net/rtk_wifi6/wlan0/bd_info
				cat /proc/net/rtk_wifi6/wlan0/int_logs
				cat /proc/net/rtk_wifi6/wlan0/rx_debug
				cat /proc/net/rtk_wifi6/wlan0/trx_info
				cat /proc/net/rtk_wifi6/wlan0/tx_logs
				cat /proc/net/rtk_wifi6/wlan0/rx_logs
				cat /proc/net/rtk_wifi6/wlan0/all_sta_info
				iwpriv wlan0 phl_test dump_cnt
				sleep 1
				cat /proc/net/rtk_wifi6/wlan0/bd_info
				cat /proc/net/rtk_wifi6/wlan0/int_logs
				cat /proc/net/rtk_wifi6/wlan0/rx_debug
				cat /proc/net/rtk_wifi6/wlan0/trx_info
				cat /proc/net/rtk_wifi6/wlan0/tx_logs
				cat /proc/net/rtk_wifi6/wlan0/rx_logs
				cat /proc/net/rtk_wifi6/wlan0/all_sta_info
				iwpriv wlan0 phl_test dump_cnt
				sleep 1
				cat /proc/net/rtk_wifi6/wlan0/bd_info
				cat /proc/net/rtk_wifi6/wlan0/int_logs
				cat /proc/net/rtk_wifi6/wlan0/rx_debug
				cat /proc/net/rtk_wifi6/wlan0/trx_info
				cat /proc/net/rtk_wifi6/wlan0/tx_logs
				cat /proc/net/rtk_wifi6/wlan0/rx_logs
				cat /proc/net/rtk_wifi6/wlan0/all_sta_info
				iwpriv wlan0 phl_test dump_cnt
				wpa_cli -g /var/run/hostapd/global.wlan0 raw REMOVE wlan0
				sleep 2
				wpa_cli -g /var/run/hostapd/global.wlan0 raw ADD bss_config=phy0:/var/hostapd.conf.wlan0
				sleep 5
				echo 0 > /proc/net/rtk_wifi6/wlan0/dfs_cac_time
			fi
		fi	
	fi

	if [ -f /proc/net/rtk_wifi6/wlan1/stats ]; then
        	recovery_detect=$(cat /proc/net/rtk_wifi6/wlan1/stats | tail -n 1 | cut -d : -f 2)
			if [ -n "$recovery_detect" ]; then
				if [ $recovery_detect = $cmd ]; then
				echo "wlan1 : recovery_detect is 1 !!!" > /dev/console
				echo 3 3 > /proc/net/rtk_wifi6/log_level
				cat /proc/net/rtk_wifi6/wlan1/bd_info
				cat /proc/net/rtk_wifi6/wlan1/int_logs
				cat /proc/net/rtk_wifi6/wlan1/rx_debug
				cat /proc/net/rtk_wifi6/wlan1/trx_info
				cat /proc/net/rtk_wifi6/wlan1/tx_logs
				cat /proc/net/rtk_wifi6/wlan1/rx_logs
				cat /proc/net/rtk_wifi6/wlan1/all_sta_info
				iwpriv wlan1 phl_test dump_cnt
				sleep 1
				cat /proc/net/rtk_wifi6/wlan1/bd_info
				cat /proc/net/rtk_wifi6/wlan1/int_logs
				cat /proc/net/rtk_wifi6/wlan1/rx_debug
				cat /proc/net/rtk_wifi6/wlan1/trx_info
				cat /proc/net/rtk_wifi6/wlan1/tx_logs
				cat /proc/net/rtk_wifi6/wlan1/rx_logs
				cat /proc/net/rtk_wifi6/wlan1/all_sta_info
				iwpriv wlan1 phl_test dump_cnt
				sleep 1
				cat /proc/net/rtk_wifi6/wlan1/bd_info
				cat /proc/net/rtk_wifi6/wlan1/int_logs
				cat /proc/net/rtk_wifi6/wlan1/rx_debug
				cat /proc/net/rtk_wifi6/wlan1/trx_info
				cat /proc/net/rtk_wifi6/wlan1/tx_logs
				cat /proc/net/rtk_wifi6/wlan1/rx_logs
				cat /proc/net/rtk_wifi6/wlan1/all_sta_info
				iwpriv wlan1 phl_test dump_cnt
				wpa_cli -g /var/run/hostapd/global.wlan1 raw REMOVE wlan1
				sleep 2
				wpa_cli -g /var/run/hostapd/global.wlan1 raw ADD bss_config=phy1:/var/hostapd.conf.wlan1
				sleep 5
			fi
		fi
	fi

	sleep 1
done
