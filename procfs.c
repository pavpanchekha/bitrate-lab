/* Added for 6.829 */

#include <linux/kernel.h>
#include <linux/proc_fs.h>

#include "procfs.h"
#include "rc.h"
#include "myglobs.h"

struct proc_dir_entry *ath_procfile;

int
ath_procfile_read(char *buffer,
                  char **buffer_location,
                  off_t offset, int buffer_length, int *eof, void *data) {
    int ret, i = 0;
    struct ath_rate_table *table = ath_get_current_rate_table();
    struct ieee80211_tx_info *info = ath_get_current_tx_info();
    struct ieee80211_tx_rate rate;

    /*
      TODO: Get `table` and `rate`
     */

    if (offset > 0) {
	ret = 0;
    } else if (table == NULL || info == NULL) {
	ret = snprintf(buffer, buffer_length, "No rate known at this time.\n");
    } else {
	ret = 0;
	for (; i < IEEE80211_TX_MAX_RATES; i++) {
	    rate = info->control.rates[i];
	    if (rate.idx == -1) {
		break;
	    }
	    ret += snprintf(buffer, buffer_length,
			    "Rate %d at %d(%d) kbps, code %d: %d tries.\n",
			    rate.idx,
			    table->info[rate.idx].ratekbps,
			    table->info[rate.idx].user_ratekbps,
			    table->info[rate.idx].ratecode,
			    rate.count);
	}
    }

    return ret;
}

int ath_init_procfile() {
    ath_procfile = create_proc_entry(ath_procfs_name, 0644, NULL);

    if (ath_procfile == NULL) {
        remove_proc_entry(ath_procfs_name, NULL);
	printk(KERN_ALERT "Error: Could not initialize /proc/%s\n",
	       ath_procfs_name);
	return -ENOMEM;
    }

    ath_procfile->read_proc = ath_procfile_read;
    ath_procfile->mode = S_IFREG | S_IRUGO;
    ath_procfile->uid = 0;
    ath_procfile->gid = 0;
    ath_procfile->size = 256;

return 0;
}

int ath_cleanup_procfile() {
    remove_proc_entry(ath_procfs_name, NULL);
    printk(KERN_INFO "/proc/%s removed\n", ath_procfs_name);
    return 0;
}
