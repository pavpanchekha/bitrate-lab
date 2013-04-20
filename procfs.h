
#include <linux/proc_fs.h>

#define ath_procfs_name "ath_rate"

struct proc_dir_entry *ath_procfile;
struct ath_rate_table *ath_current_rate_table;
struct ieee80211_tx_info *ath_current_tx_info;

int
ath_procfile_read(char *buffer,
                  char **buffer_location,
                  off_t offset, int buffer_length, int *eof, void *data);

int ath_init_procfile();
int ath_cleanup_procfile();
