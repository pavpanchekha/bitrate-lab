#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

MODULE_INFO(intree, "Y");

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x915a5725, "module_layout" },
	{ 0xad4e683c, "ath9k_hw_set_txq_props" },
	{ 0x79d579b2, "ath9k_hw_init" },
	{ 0xca19f9e7, "kmalloc_caches" },
	{ 0xbc83b659, "ath9k_hw_deinit" },
	{ 0x333fad3b, "ath9k_hw_cfg_output" },
	{ 0x68e2f221, "_raw_spin_unlock" },
	{ 0x15692c87, "param_ops_int" },
	{ 0x426fe298, "device_release_driver" },
	{ 0xaeeb1a56, "ath9k_hw_set_gpio" },
	{ 0x2837ac5f, "ath9k_cmn_init_crypto" },
	{ 0x76a19f9f, "ieee80211_queue_work" },
	{ 0x9bd60b6d, "dev_set_drvdata" },
	{ 0xe6dc2bd0, "led_classdev_register" },
	{ 0x6f0d109d, "ath9k_hw_btcoex_enable" },
	{ 0x7f655864, "ath9k_hw_wait" },
	{ 0x3fcdb486, "ath9k_cmn_get_hw_crypto_keytype" },
	{ 0x8ddf2d62, "ath9k_hw_stopdmarecv" },
	{ 0xe506901b, "ath_key_delete" },
	{ 0xddc97902, "ath9k_cmn_update_txpow" },
	{ 0xa4eb4eff, "_raw_spin_lock_bh" },
	{ 0x6b06fdce, "delayed_work_timer_fn" },
	{ 0xb75056d9, "ieee80211_beacon_get_tim" },
	{ 0xe96e27f, "ath9k_hw_gpio_get" },
	{ 0xd46788d9, "ath_regd_init" },
	{ 0x4205ad24, "cancel_work_sync" },
	{ 0x7f08aec3, "usb_kill_urb" },
	{ 0xe2fae716, "kmemdup" },
	{ 0xf7e3ed1e, "ath9k_cmn_get_curchannel" },
	{ 0xee7bc042, "ieee80211_unregister_hw" },
	{ 0xeae3dfd6, "__const_udelay" },
	{ 0x593a99b, "init_timer_key" },
	{ 0x6a417ef4, "cancel_delayed_work_sync" },
	{ 0xf6e8c154, "mutex_unlock" },
	{ 0x66680d44, "ieee80211_iterate_active_interfaces_atomic" },
	{ 0x60d4a5e9, "ath9k_hw_setrxfilter" },
	{ 0x3d33cc76, "ath9k_hw_get_txq_props" },
	{ 0x3e4bfb5c, "ath9k_hw_releasetxqueue" },
	{ 0x76d72133, "ath9k_hw_reset_tsf" },
	{ 0x723ca244, "wiphy_rfkill_start_polling" },
	{ 0x7d11c268, "jiffies" },
	{ 0x16009eec, "skb_trim" },
	{ 0xf3ee2b74, "ieee80211_stop_queues" },
	{ 0x810454d9, "usb_unanchor_urb" },
	{ 0xf3689d7d, "__netdev_alloc_skb" },
	{ 0x78342dbd, "ieee80211_tx_status" },
	{ 0x58f8c21b, "ath_printk" },
	{ 0x68dfc59f, "__init_waitqueue_head" },
	{ 0xf60095fd, "ath9k_hw_setopmode" },
	{ 0x3fa58ef8, "wait_for_completion" },
	{ 0x99ff06ce, "ath9k_hw_disable" },
	{ 0xd5f2172f, "del_timer_sync" },
	{ 0x233232e7, "ath9k_hw_resettxqueue" },
	{ 0xffb9153e, "ath9k_hw_gettsf64" },
	{ 0x962fc650, "dev_err" },
	{ 0xf97456ea, "_raw_spin_unlock_irqrestore" },
	{ 0x37befc70, "jiffies_to_msecs" },
	{ 0x95002808, "usb_deregister" },
	{ 0xcdb83819, "__mutex_init" },
	{ 0x50eedeb8, "printk" },
	{ 0x295b4000, "ath9k_hw_set_sta_beacon_timers" },
	{ 0x65777f51, "ath9k_hw_set_tsfadjust" },
	{ 0x315762b6, "ieee80211_wake_queues" },
	{ 0xfaef0ed, "__tasklet_schedule" },
	{ 0x6b6947d0, "ath9k_hw_btcoex_disable" },
	{ 0x5f634591, "ath9k_hw_getrxfilter" },
	{ 0xa94d13b3, "ath9k_hw_ani_monitor" },
	{ 0xb4390f9a, "mcount" },
	{ 0xb838f02d, "usb_control_msg" },
	{ 0x6c2e3320, "strncmp" },
	{ 0x4e2481d5, "ath_is_world_regd" },
	{ 0x16305289, "warn_slowpath_null" },
	{ 0x687f824e, "ieee80211_rx" },
	{ 0x16463bfa, "skb_push" },
	{ 0x85a39699, "mutex_lock" },
	{ 0x9545af6d, "tasklet_init" },
	{ 0x8834396c, "mod_timer" },
	{ 0x2469810f, "__rcu_read_unlock" },
	{ 0x8067a97f, "skb_pull" },
	{ 0xb799f651, "wiphy_rfkill_stop_polling" },
	{ 0x294c7f9d, "request_firmware_nowait" },
	{ 0x59275983, "ath9k_cmn_update_ichannel" },
	{ 0x1115907c, "ath9k_hw_write_associd" },
	{ 0x6d30f8e, "ieee80211_queue_delayed_work" },
	{ 0xbfce3760, "dev_kfree_skb_any" },
	{ 0xf11543ff, "find_first_zero_bit" },
	{ 0xb9cccbbb, "ath_reg_notifier_apply" },
	{ 0xf91d30c8, "wiphy_to_ieee80211_hw" },
	{ 0x82072614, "tasklet_kill" },
	{ 0xaab002f5, "ath9k_hw_init_btcoex_hw" },
	{ 0x45a46abc, "ieee80211_stop_tx_ba_cb_irqsafe" },
	{ 0xe85d731e, "skb_queue_tail" },
	{ 0xb72afe04, "ath9k_hw_beaconq_setup" },
	{ 0x74ae9380, "_dev_info" },
	{ 0x336a5b70, "usb_submit_urb" },
	{ 0xe74dbf5c, "ath9k_hw_name" },
	{ 0x5632bb89, "ath9k_hw_init_global_settings" },
	{ 0x590f920f, "__alloc_skb" },
	{ 0x40041c8c, "usb_get_dev" },
	{ 0x8c4db1b5, "usb_kill_anchored_urbs" },
	{ 0xd2981357, "ath9k_cmn_count_streams" },
	{ 0x3907de89, "ath9k_hw_settsf64" },
	{ 0x8bf826c, "_raw_spin_unlock_bh" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0xe3a9d8c, "wiphy_rfkill_set_hw_state" },
	{ 0x3bd1b1f6, "msecs_to_jiffies" },
	{ 0x2862929a, "usb_bulk_msg" },
	{ 0x47beaeed, "usb_put_dev" },
	{ 0x86a4889a, "kmalloc_order_trace" },
	{ 0xb792ab72, "kfree_skb" },
	{ 0x5bf5671, "ath9k_hw_beaconinit" },
	{ 0xdfcdd9ee, "ieee80211_find_sta" },
	{ 0x4eeea74a, "ieee80211_get_buffered_bc" },
	{ 0x55cd93c, "ath9k_hw_btcoex_bt_stomp" },
	{ 0x3cae9963, "ath9k_hw_setrxabort" },
	{ 0x30b0f48d, "kmem_cache_alloc_trace" },
	{ 0x67f7403e, "_raw_spin_lock" },
	{ 0xc2ca0625, "ath_hw_setbssidmask" },
	{ 0x21fb443e, "_raw_spin_lock_irqsave" },
	{ 0xf59eadf3, "ath9k_cmn_padpos" },
	{ 0x29147913, "ath9k_hw_phy_disable" },
	{ 0xd3749896, "ieee80211_get_hdrlen_from_skb" },
	{ 0xa4f4bfa7, "ath9k_hw_setpower" },
	{ 0xbebeff8a, "__ieee80211_create_tpt_led_trigger" },
	{ 0x35b48615, "ieee80211_register_hw" },
	{ 0xcd5b0bb7, "led_classdev_unregister" },
	{ 0xc985160d, "ath9k_hw_btcoex_set_weight" },
	{ 0x37a0cba, "kfree" },
	{ 0x31765770, "regulatory_hint" },
	{ 0x2e60bace, "memcpy" },
	{ 0x7e8a3604, "ath9k_hw_setmcastfilter" },
	{ 0x7344e354, "ieee80211_start_tx_ba_session" },
	{ 0xf6412ca4, "ieee80211_alloc_hw" },
	{ 0x4254b99c, "ath9k_hw_startpcureceive" },
	{ 0x6ea70a69, "ath9k_hw_setuptxqueue" },
	{ 0xb1c6e40, "usb_register_driver" },
	{ 0x3be7faf0, "request_firmware" },
	{ 0xe73c0067, "ath9k_hw_reset" },
	{ 0xc6280508, "ieee80211_free_hw" },
	{ 0xa2ba25ac, "skb_dequeue" },
	{ 0x13d521d9, "usb_ifnum_to_if" },
	{ 0x19a9e62b, "complete" },
	{ 0xb81960ca, "snprintf" },
	{ 0x8235805b, "memmove" },
	{ 0x916008e9, "ath9k_hw_btcoex_init_3wire" },
	{ 0x356030e, "ath_key_config" },
	{ 0x8d522714, "__rcu_read_lock" },
	{ 0x29558dba, "skb_put" },
	{ 0xb1d9523e, "wait_for_completion_timeout" },
	{ 0x6d044c26, "param_ops_uint" },
	{ 0x690f2189, "ath9k_hw_reset_calvalid" },
	{ 0x12696590, "dev_get_drvdata" },
	{ 0xea5b03c, "usb_free_urb" },
	{ 0x54f56679, "release_firmware" },
	{ 0x484f8b81, "ieee80211_start_tx_ba_cb_irqsafe" },
	{ 0xcf6705e7, "usb_anchor_urb" },
	{ 0xde45d228, "usb_alloc_urb" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=ath9k_hw,ath9k_common,mac80211,ath,usbcore,cfg80211";

MODULE_ALIAS("usb:v0CF3p9271d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0CF3p1006d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0846p9030d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v07D1p3A10d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v13D3p3327d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v13D3p3328d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v13D3p3346d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v13D3p3348d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v13D3p3349d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v13D3p3350d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v04CAp4605d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v040Dp3801d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0CF3pB003d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0CF3pB002d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v057Cp8403d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0CF3p7015d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v1668p1200d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0CF3p7010d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0846p9018d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v083ApA704d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0411p017Fd*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v04DAp3904d*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v0CF3p20FFd*dc*dsc*dp*ic*isc*ip*in*");
