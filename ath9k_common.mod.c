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
	{ 0xb4390f9a, "mcount" },
	{ 0x21a3c55c, "ath_hw_keyreset" },
	{ 0xe9cc0151, "ath9k_hw_set_txpowerlimit" },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=ath,ath9k_hw";

