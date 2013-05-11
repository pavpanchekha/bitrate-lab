/* Some stuff for 6.829 */

#include <linux/time.h>
#include "myglobs.h"
#include "ath9k.h"

struct mutex ath_myglobs_mutex;

char ath_stats_buffer[8192][128];
int ath_stats_buffer_idx;

struct ath_rate_table *ath_current_rate_table = 0;
struct ieee80211_tx_info *ath_current_tx_info = 0;

struct timespec ath_packet_send_start = { 0 };
struct timespec ath_packet_init_start = { 0 };
u8 ath_packet_send_rate = 0;

static u8 ath_rotating_rix = 0;

void ath_myglobs_init() {
  ath_stats_buffer_idx = 0;
  getnstimeofday(&ath_packet_init_start);
  mutex_init(&ath_myglobs_mutex);
}

void ath_myglobs_lock() {
  mutex_lock(&ath_myglobs_mutex);
}

void ath_myglobs_unlock() {
  mutex_unlock(&ath_myglobs_mutex);
}

struct ath_rate_table *ath_get_current_rate_table() {
  return ath_current_rate_table;
}

void ath_set_current_rate_table(struct ath_rate_table *table) {
  ath_current_rate_table = table;
}

struct ieee80211_tx_info *ath_get_current_tx_info() {
  return ath_current_tx_info;
}

void ath_set_current_tx_info(struct ieee80211_tx_info *tx_info) {
  ath_current_tx_info = tx_info;
}

void ath_set_on_send() {
  struct timespec now;
  getnstimeofday(&now);
  ath_packet_send_start = timespec_sub(now, ath_packet_init_start);

  if (ath_current_tx_info == 0) {
      // do nothing, keep send rate at 0
  } else {
      ath_packet_send_rate = ath_current_tx_info->control.rates[0].idx;
  }
}

u8 ath_get_rotating_rix() {
  return ath_rotating_rix;
}

void ath_set_on_complete() {
  struct timespec ath_packet_send_end;
  struct timespec diff;
  u8 ath_packet_send_retries;

  ath_rotating_rix = (ath_rotating_rix + 1) % 12;

  getnstimeofday(&ath_packet_send_end);
  diff = timespec_sub(ath_packet_send_end, ath_packet_send_start);

  if (ath_current_tx_info == 0) {
    //do nothing, keep tries at 0
    ath_packet_send_retries = 0;
  } else {
    ath_packet_send_retries = \
      ath_current_tx_info->control.rates[0].count + \
      ath_current_tx_info->control.rates[1].count;
  }

  ath_set_buffer(ath_packet_send_start,
                 diff.tv_sec * 1000000000LL + diff.tv_nsec,
                 ath_packet_send_retries);
}

void ath_set_buffer(struct timespec id, unsigned long long diff, u8 retries) {
  ath_myglobs_lock();
  if (ath_stats_buffer_idx < sizeof(ath_stats_buffer) / sizeof(ath_stats_buffer[0])) {
    ath_stats_to_str(ath_stats_buffer[ath_stats_buffer_idx], 128,
                     id, diff, retries);
    ath_stats_buffer_idx++;
  }
  ath_myglobs_unlock();
}


int ath_stats_to_str(char *buffer, size_t buffer_length,
                     struct timespec id, unsigned long long diff, u8 retries) {
  struct ath_rate_table *table = ath_get_current_rate_table();
  int i, ret;
  ret = 0;

  if (table == NULL) {
   buffer[0] = '\0';
    return 0;
  }

  i  = ath_packet_send_rate;

  ret = snprintf(buffer, buffer_length,
                 "Last(%l:%l.%lu) took %llu ns / %d tries with rate %d at %d(%d) kbps [%d]\n",
                 id.tv_min, id.tv_sec, id.tv_nsec,
                 diff,
                 retries,
                 i,
                 table->info[i].ratekbps,
                 table->info[i].user_ratekbps,
                 ath_stats_buffer_idx);

  if (ret >= buffer_length) {
    buffer[buffer_length] = '\0';
  }

  return ret;
}

int ath_get_buffer(char *buffer, size_t buffer_length) {
  int i, ret;
  ret = 0;
  
  ath_myglobs_lock();
  for (i = 0; i < ath_stats_buffer_idx; i++) {
    ret += snprintf(buffer + ret, buffer_length - ret,
                    "%s", ath_stats_buffer[i]);
  }
  ath_stats_buffer_idx = 0;
  ath_myglobs_unlock();

  return ret;
}
