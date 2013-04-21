
#pragma once
#ifndef ATH_PROCFS_H
#define ATH_PROCFS_H
#include <linux/proc_fs.h>

#define ath_procfs_name "ath_rate"

int
ath_procfile_read(char *buffer,
                  char **buffer_location,
                  off_t offset, int buffer_length, int *eof, void *data);

int ath_init_procfile(void);
int ath_cleanup_procfile(void);

#endif
