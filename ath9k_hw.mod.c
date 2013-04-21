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
	{ 0xca19f9e7, "kmalloc_caches" },
	{ 0x12da5bb2, "__kmalloc" },
	{ 0xeae3dfd6, "__const_udelay" },
	{ 0x58f8c21b, "ath_printk" },
	{ 0x2bc95bd4, "memset" },
	{ 0xb4390f9a, "mcount" },
	{ 0x16305289, "warn_slowpath_null" },
	{ 0x4fe8f6de, "ath_hw_get_listen_time" },
	{ 0x53358ce3, "ath_regd_get_band_ctl" },
	{ 0xf0fdf6cb, "__stack_chk_fail" },
	{ 0x579fbcd2, "cpu_possible_mask" },
	{ 0x12769e39, "ath_hw_cycle_counters_update" },
	{ 0x30b0f48d, "kmem_cache_alloc_trace" },
	{ 0xc2ca0625, "ath_hw_setbssidmask" },
	{ 0x37a0cba, "kfree" },
	{ 0x2e60bace, "memcpy" },
	{ 0x74c134b9, "__sw_hweight32" },
	{ 0xb81960ca, "snprintf" },
	{ 0x9e7d6bd0, "__udelay" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=ath";

