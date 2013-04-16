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
	{ 0x7e001291, "module_layout" },
	{ 0x2798f095, "ath9k_hw_set_txq_props" },
	{ 0x3b73194d, "ath9k_hw_init" },
	{ 0xe5a7e546, "kmalloc_caches" },
	{ 0x48c2d371, "ath9k_hw_deinit" },
	{ 0xce1cdc8a, "ath9k_hw_cfg_output" },
	{ 0x68e2f221, "_raw_spin_unlock" },
	{ 0x3ec8886f, "param_ops_int" },
	{ 0x85df8ff, "ath9k_hw_set_gpio" },
	{ 0xf343efe4, "ath9k_cmn_init_crypto" },
	{ 0x84c6c34a, "ieee80211_queue_work" },
	{ 0x298752af, "dev_set_drvdata" },
	{ 0x9aaa7783, "led_classdev_register" },
	{ 0x5e70307, "ath9k_hw_btcoex_enable" },
	{ 0x2a3fa148, "ath9k_hw_wait" },
	{ 0x8a24ad03, "ath9k_cmn_get_hw_crypto_keytype" },
	{ 0x495a3359, "ath_key_delete" },
	{ 0xcc9565a3, "ath9k_cmn_update_txpow" },
	{ 0xa4eb4eff, "_raw_spin_lock_bh" },
	{ 0x39a5b563, "ieee80211_beacon_get_tim" },
	{ 0x7291f959, "ath9k_hw_gpio_get" },
	{ 0x51503128, "ath_regd_init" },
	{ 0x4205ad24, "cancel_work_sync" },
	{ 0x14ee782, "usb_kill_urb" },
	{ 0xe2fae716, "kmemdup" },
	{ 0x9142e024, "ath9k_cmn_get_curchannel" },
	{ 0xac3f78f0, "ieee80211_unregister_hw" },
	{ 0xeae3dfd6, "__const_udelay" },
	{ 0xfb0e29f, "init_timer_key" },
	{ 0x6baae653, "cancel_delayed_work_sync" },
	{ 0x5839cf92, "mutex_unlock" },
	{ 0xf830332a, "ieee80211_iterate_active_interfaces_atomic" },
	{ 0x35ee5e4a, "ath9k_hw_setrxfilter" },
	{ 0xb847a5b3, "ath9k_hw_get_txq_props" },
	{ 0x6f7db398, "ath9k_hw_releasetxqueue" },
	{ 0x10878f6a, "ath9k_hw_reset_tsf" },
	{ 0x451edd48, "wiphy_rfkill_start_polling" },
	{ 0x12d3198f, "ath9k_hw_cfg_gpio_input" },
	{ 0x7d11c268, "jiffies" },
	{ 0x5465a0b2, "skb_trim" },
	{ 0x73f69715, "ieee80211_stop_queues" },
	{ 0xb1be814f, "usb_unanchor_urb" },
	{ 0x456e4518, "ieee80211_tx_status" },
	{ 0x900d9db9, "ath_printk" },
	{ 0x68dfc59f, "__init_waitqueue_head" },
	{ 0x2be6f618, "ath9k_hw_setopmode" },
	{ 0xf58089e6, "ath9k_hw_disable" },
	{ 0xd5f2172f, "del_timer_sync" },
	{ 0x33fb9400, "ath9k_hw_resettxqueue" },
	{ 0x23714385, "ath9k_hw_gettsf64" },
	{ 0xd941fb89, "dev_err" },
	{ 0xf97456ea, "_raw_spin_unlock_irqrestore" },
	{ 0x37befc70, "jiffies_to_msecs" },
	{ 0xe2b26072, "usb_deregister" },
	{ 0x919aab8b, "__mutex_init" },
	{ 0x50eedeb8, "printk" },
	{ 0x737b213d, "ath9k_hw_set_sta_beacon_timers" },
	{ 0x62a3e13c, "ath9k_hw_set_tsfadjust" },
	{ 0x18f1a86, "ieee80211_wake_queues" },
	{ 0xfaef0ed, "__tasklet_schedule" },
	{ 0x4ff83d15, "ath9k_hw_btcoex_disable" },
	{ 0x5ec402b3, "ath9k_hw_getrxfilter" },
	{ 0x792bdecb, "ath9k_hw_ani_monitor" },
	{ 0xb4390f9a, "mcount" },
	{ 0xd231b5f9, "usb_control_msg" },
	{ 0x6c2e3320, "strncmp" },
	{ 0x4e2481d5, "ath_is_world_regd" },
	{ 0x16305289, "warn_slowpath_null" },
	{ 0xe55c4e6b, "ieee80211_rx" },
	{ 0x8fcc9ff0, "skb_push" },
	{ 0x4a8810d4, "mutex_lock" },
	{ 0x9545af6d, "tasklet_init" },
	{ 0x8834396c, "mod_timer" },
	{ 0x2469810f, "__rcu_read_unlock" },
	{ 0x86c3da8, "skb_pull" },
	{ 0xa1bb881f, "wiphy_rfkill_stop_polling" },
	{ 0x40d3a2e4, "ath9k_cmn_update_ichannel" },
	{ 0xe664d583, "ath9k_hw_write_associd" },
	{ 0xe37afd8c, "ieee80211_queue_delayed_work" },
	{ 0x883c3785, "dev_kfree_skb_any" },
	{ 0xf11543ff, "find_first_zero_bit" },
	{ 0x5d9f1b20, "ath_reg_notifier_apply" },
	{ 0xf84e48b1, "ath9k_hw_htc_resetinit" },
	{ 0x36f6ff23, "wiphy_to_ieee80211_hw" },
	{ 0x82072614, "tasklet_kill" },
	{ 0x663cd5, "ath9k_hw_init_btcoex_hw" },
	{ 0x17217a33, "ieee80211_stop_tx_ba_cb_irqsafe" },
	{ 0x5988a5e, "skb_queue_tail" },
	{ 0x3f69b26f, "ath9k_hw_beaconq_setup" },
	{ 0xd7ef3d2f, "_dev_info" },
	{ 0x77e72255, "usb_submit_urb" },
	{ 0x7c6cd66e, "ath9k_hw_name" },
	{ 0x641b2f2f, "ath9k_hw_disable_mib_counters" },
	{ 0x9ef0fe68, "ath9k_hw_init_global_settings" },
	{ 0x4627b5f8, "__alloc_skb" },
	{ 0xf5cb3205, "usb_get_dev" },
	{ 0x8c4db1b5, "usb_kill_anchored_urbs" },
	{ 0xd2981357, "ath9k_cmn_count_streams" },
	{ 0xcff15024, "ath9k_hw_settsf64" },
	{ 0x8bf826c, "_raw_spin_unlock_bh" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0xb2d8ff0f, "wiphy_rfkill_set_hw_state" },
	{ 0x3bd1b1f6, "msecs_to_jiffies" },
	{ 0x8b536cff, "usb_bulk_msg" },
	{ 0x4a49f104, "usb_put_dev" },
	{ 0x86a4889a, "kmalloc_order_trace" },
	{ 0x3602cea, "kfree_skb" },
	{ 0xa157c318, "ath9k_hw_beaconinit" },
	{ 0xc06602ac, "ieee80211_find_sta" },
	{ 0xe883c42d, "ieee80211_get_buffered_bc" },
	{ 0xf1e8863b, "ath9k_hw_btcoex_bt_stomp" },
	{ 0x82091bc4, "kmem_cache_alloc_trace" },
	{ 0x67f7403e, "_raw_spin_lock" },
	{ 0x6da81fb4, "ath_hw_setbssidmask" },
	{ 0x21fb443e, "_raw_spin_lock_irqsave" },
	{ 0xf59eadf3, "ath9k_cmn_padpos" },
	{ 0xa69f88de, "ath9k_hw_phy_disable" },
	{ 0x1d9a223b, "ieee80211_get_hdrlen_from_skb" },
	{ 0x6fa43f1, "ath9k_hw_setpower" },
	{ 0x4a67ebcf, "__ieee80211_create_tpt_led_trigger" },
	{ 0xe785d475, "ieee80211_register_hw" },
	{ 0xb2543ef8, "led_classdev_unregister" },
	{ 0xd731ba5f, "ath9k_hw_btcoex_set_weight" },
	{ 0x37a0cba, "kfree" },
	{ 0xd03d9fb, "regulatory_hint" },
	{ 0x2e60bace, "memcpy" },
	{ 0xe8086076, "ath9k_hw_setmcastfilter" },
	{ 0x4fb39646, "ieee80211_start_tx_ba_session" },
	{ 0xfe56b484, "ieee80211_alloc_hw" },
	{ 0x40f5a0b1, "ath9k_hw_startpcureceive" },
	{ 0x7bec8dd2, "ath9k_hw_setuptxqueue" },
	{ 0xed094f03, "usb_register_driver" },
	{ 0x58174fb7, "request_firmware" },
	{ 0xf6479f50, "ath9k_hw_reset" },
	{ 0x1c39dd8d, "ieee80211_free_hw" },
	{ 0x6802505, "skb_dequeue" },
	{ 0xff8a04e1, "usb_ifnum_to_if" },
	{ 0x19a9e62b, "complete" },
	{ 0xb81960ca, "snprintf" },
	{ 0x8235805b, "memmove" },
	{ 0x552eb2ee, "ath9k_hw_btcoex_init_3wire" },
	{ 0xc75b78e6, "ath_key_config" },
	{ 0x8d522714, "__rcu_read_lock" },
	{ 0x95a63888, "skb_put" },
	{ 0xb1d9523e, "wait_for_completion_timeout" },
	{ 0xc3fe87c8, "param_ops_uint" },
	{ 0xdb67339a, "ath9k_hw_reset_calvalid" },
	{ 0xe587928, "dev_get_drvdata" },
	{ 0x8247c0e8, "usb_free_urb" },
	{ 0xcd433b97, "release_firmware" },
	{ 0x5d64ede4, "ieee80211_start_tx_ba_cb_irqsafe" },
	{ 0x483ebae5, "usb_anchor_urb" },
	{ 0x4c66cbd2, "usb_alloc_urb" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=ath9k_hw,ath9k_common,mac80211,ath,usbcore,cfg80211";

MODULE_ALIAS("usb:v0CF3p9271d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0CF3p1006d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0846p9030d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v07D1p3A10d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v13D3p3327d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v13D3p3328d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v13D3p3346d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v13D3p3348d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v13D3p3349d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v13D3p3350d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v04CAp4605d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v040Dp3801d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0CF3pB003d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v057Cp8403d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0CF3p7015d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v1668p1200d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0CF3p7010d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0846p9018d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v083ApA704d*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0411p017Fd*dc*dsc*dp*ic*isc*ip*");
MODULE_ALIAS("usb:v0CF3p20FFd*dc*dsc*dp*ic*isc*ip*");
