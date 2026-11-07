RTK_OFDMA_DISABLE=0
RTK_OFDMA_UL_ENABLE=2
RTK_OFDMA_DL_ENABLE=8

rtk_wlan_phy_cal() {
	local ifname="$1"
	
	if [ ! -d "/sys/class/net/${ifname}" ]; then
		return
	fi
	
	wlan_cal $ifname
}

rtk_detect_mac80211() {
	local phy="$1"

	if [ "$mode_band" = "5g" ]; then
		if [ "$(iw phy $phy info | grep -c HE160)" -gt 0 ]; then
			htmode="HE160"
		fi
	fi
}

rtk_mac80211_init_device_config() {
	config_add_boolean amsdu
	config_add_boolean txbf txbf_mu
	config_add_int ofdma
}

rtk_mac80211_init_iface_config() {
	echo "TODO"
}

rtk_hostapd_common_add_device_config() {
	echo "TODO"
}

rtk_hostapd_common_add_bss_config() {
	echo "TODO"
}

rtk_hostapd_set_wpa_pairwise() {

	case "$auth_type" in
		eap192)
			wpa_pairwise=GCMP-256
		;;
	esac
}

rtk_hostapd_set_group_mgmt_cipher() {

	case "$auth_type" in
		eap192)
			ieee80211w_mgmt_cipher=BIP-GMAC-256
		;;
	esac
}

rtk_hostapd_append_wpa_key_mgmt() {

	case "$auth_type" in
		psk|eap)
			[ "${ieee80211w:-0}" -eq 2 ] && wpa_key_mgmt="WPA-${auth_type_l}-SHA256"
		;;
	esac
}

rtk_hostapd_set_default() {
	set_default bss_load_update_period 0
}

rtk_brsnoop_isolation_set_default() {
	set_default multicast_to_unicast 0
}

rtk_mac80211_hostapd_setup_base() {
	json_get_vars country
	
	echo "$auto_channel, $htmode, $country" >> /var/log/debug.log
	[ "$auto_channel" -gt 0 ] && [ "$htmode" = "HE160" ] && [ "$country" = "US" ] && \
		channel_list="36-48"
}

rtk_mac80211_hostapd_remove_start_disabled() {

	[ "$start_disabled" -eq 0 ] &&  sed -i '/start_disabled/d' /var/run/hostapd-$phy.conf
}

rtk_mac80211_chan_width_check() {

	[ "$vht_oper_chwidth" -ne 2 ] && vht160=0
}

rtk_mac80211_phy_oob_config() {
	local primary_ap=$1

	json_select config
	json_get_vars amsdu txbf txbf_mu ofdma
	json_get_vars noscan ht_coex
	json_select ..

	rtk_wlan_phy_cal $primary_ap

	set_default amsdu 1
	set_default txbf 1
	set_default txbf_mu 0
	set_default ofdma 0
	set_default noscan 0
	set_default ht_coex 0

	if [ -n "$primary_ap" ]; then
		iwpriv $primary_ap set_mib amsdu=$amsdu
		iwpriv $primary_ap set_mib txbf=$txbf
		iwpriv $primary_ap set_mib txbf_mu=$txbf_mu

		if [ "$noscan" -eq 0 -a "$ht_coex" -eq 1 ]; then
			iwpriv $primary_ap set_mib coexist=1
		else
			iwpriv $primary_ap set_mib coexist=0
		fi

		case "$ofdma" in
		$RTK_OFDMA_DISABLE)
			iwpriv $primary_ap set_mib force_fw_tx=0
			iwpriv $primary_ap set_mib ofdma_enable=$ofdma
			;;
		$RTK_OFDMA_UL_ENABLE|$RTK_OFDMA_DL_ENABLE)
			iwpriv $primary_ap set_mib force_fw_tx=1
			iwpriv $primary_ap set_mib ofdma_enable=$ofdma
			;;
		*)
			logger -p user.info -t "netifd.wireless.mac80211" "Invalid ofdma value for $ifname."
			;;
		esac
	fi
}

rtk_mac80211_interface_oob_config() {
	echo "TODO"
}

rtk_hostapd_wps_led_control_setup() {
	local phy="$1"
	local ifname
	local wps_pushbutton

	json_select data
	json_get_vars ifname
	json_select ..

	json_select config
	json_get_vars wps_pushbutton
	json_select ..

	set_default wps_pushbutton 0
	if [ "$wps_pushbutton" -eq 0 ]; then
		logger -p user.info -t "netifd.wireless.mac80211" "Skip for $ifname wps led control."
		return
	fi

	if [ -f /etc/hostapd_wps_led.sh ]; then
		/usr/sbin/hostapd_cli -a /etc/hostapd_wps_led.sh -B \
			-P /var/run/hostapd_cli.pid.$ifname.wps -i $ifname
		wireless_add_process "$(cat /var/run/hostapd_cli.pid.$ifname.wps)" \
			"/usr/sbin/hostapd_cli" 1
	fi
}

rtk_wpas_wps_led_control_setup() {
	local phy="$1"
	local ifname
	local wps_pushbutton

	json_select data
	json_get_vars ifname
	json_select ..

	if [ -f /etc/wpa_supplicant_wps_led.sh ]; then
		/usr/sbin/wpa_cli -a /etc/wpa_supplicant_wps_led.sh -B \
			-P /var/run/wpa_cli.pid.$ifname.wps -i $ifname
		wireless_add_process "$(cat /var/run/wpa_cli.pid.$ifname.wps)" \
			"/usr/sbin/wpa_cli" 1
	fi
}

rtk_wps_led_control_teardown() {
	local phy

	json_select data
	json_get_vars phy
	json_select ..

	[ -f /etc/hostapd_wps_led.sh ] && /etc/hostapd_wps_led.sh wlan${phy#phy} SYSTEM-WPS-STOP
	[ -f /etc/wpa_supplicant_wps_led.sh ] && /etc/wpa_supplicant_wps_led.sh wlan${phy#phy} SYSTEM-WPS-STOP
}
