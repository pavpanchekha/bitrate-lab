/* Some stuff for 6.829 */

#include <linux/interrupt.h>
#include "rc.h"

void ath_myglobs_init(void);
void ath_myglobs_lock(void);
void ath_myglobs_unlock(void);

struct ath_rate_table *ath_get_current_rate_table(void);
void ath_set_current_rate_table(struct ath_rate_table *);

struct ieee80211_tx_info *ath_get_current_tx_info(void);
void ath_set_current_tx_info(struct ieee80211_tx_info *);

void ath_set_on_send(void);
void ath_set_on_complete(void);
unsigned long ath_get_send_id(void);
unsigned long ath_get_send_diff(void);
u8 ath_get_send_rate(void);
u8 ath_get_send_tries(void);

void ath_inc_rotating_rix(void);
u8 ath_get_rotating_rix(void);

int ath_stats_to_str(char *, size_t);
void ath_set_buffer(void);
int ath_get_buffer(char *, size_t);
