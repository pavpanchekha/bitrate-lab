/* Some stuff for 6.829 */

struct ath_rate_table *ath_get_current_rate_table(void);
void ath_set_current_rate_table(struct ath_rate_table *);

struct ieee80211_tx_info *ath_get_current_tx_info(void);
void ath_set_current_tx_info(struct ieee80211_tx_info *);
