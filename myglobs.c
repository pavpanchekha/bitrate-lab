/* Some stuff for 6.829 */

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
