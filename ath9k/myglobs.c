/* Some stuff for 6.829 */

#include <linux/time.h>
#include "myglobs.h"

struct ath_rate_table *ath_current_rate_table = 0;
struct ieee80211_tx_info *ath_current_tx_info = 0;

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

struct timespec ath_packet_send_start = { 0 };
struct timespec ath_packet_send_end = { 0 };
struct timespec ath_packet_send_id = { 0 };
unsigned long ath_packet_send_diff = 0;
u8 ath_packet_send_rate = 0;
u8 ath_packet_send_retries = 0;

void ath_set_on_send() {
  getnstimeofday(&ath_packet_send_start);
  if (ath_current_tx_info == 0) {
      // do nothing, keep send rate at 0
  } else {
      ath_packet_send_rate = ath_current_tx_info->control.rates[0].idx;
  }
}

void ath_set_on_complete() {
  struct timespec diff;
  getnstimeofday(&ath_packet_send_end);
  diff = timespec_sub(ath_packet_send_end, ath_packet_send_start);
  ath_packet_send_id = ath_packet_send_start;
  ath_packet_send_diff = diff.tv_sec * 1000000000L + diff.tv_nsec;
  if (ath_current_tx_info == 0) {
    //do nothing, keep tries at 0
  } else {
    ath_packet_send_retries = ath_current_tx_info->control.rates[0].count;
  }
  ath_inc_rotating_rix();
}

unsigned long ath_get_send_id() {
  return ath_packet_send_id.tv_sec * 1000000000L + ath_packet_send_id.tv_nsec;
}

unsigned long ath_get_send_diff() {
  return ath_packet_send_diff;
}

u8 ath_get_send_tries() {
  return ath_packet_send_retries;
}

u8 ath_get_send_rate() {
  return ath_packet_send_rate;
}

static u8 ath_rotating_rix = 0;

void ath_inc_rotating_rix() {
  if (ath_current_rate_table != 0 && ath_rotating_rix < ath_current_rate_table->rate_cnt - 0) {
    ath_rotating_rix++;
  } else {
    ath_rotating_rix = 0;
  }
}

u8 ath_get_rotating_rix() {
  return ath_rotating_rix;
}
