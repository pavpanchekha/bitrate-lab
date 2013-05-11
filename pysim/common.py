import collections
import math

BitRate = collections.namedtuple("BitRate", ["phy", "kbps", "user_kbps",
                                             "code", "dot11_rate"])

RATES = [
    BitRate("cck", 1000, 900, 0, 2),
    BitRate("cck", 2000, 1900, 1, 4),
    BitRate("cck", 5500, 4900, 2, 11),
    BitRate("cck", 11000, 8100, 3, 22),
    BitRate("ofdm", 6000, 5400, 4, 12),
    BitRate("ofdm", 9000, 7800, 5, 18),
    BitRate("ofdm", 12000, 10100, 6, 24),
    BitRate("ofdm", 18000, 14100, 7, 36),
    BitRate("ofdm", 24000, 17700, 8, 48),
    BitRate("ofdm", 36000, 23700, 9, 72),
    BitRate("ofdm", 48000, 27400, 10, 96),
    BitRate("ofdm", 54000, 30900, 11, 108),

    # Ignored by some bit rate protocols
    BitRate("ht_ss", 6500, 6400, 0, 0),
    BitRate("ht_ss", 13000, 12700, 1, 1),
    BitRate("ht_ss", 19500, 18800, 2, 2),
    BitRate("ht_ss", 26000, 25000, 3, 3),
    BitRate("ht_ss", 39000, 36700, 4, 4),
    BitRate("ht_ss", 52000, 48100, 5, 5),
    BitRate("ht_ss", 58500, 53500, 6, 6),
    BitRate("ht_ss", 65000, 59000, 7, 7),
    BitRate("ht_hgi", 72200, 65400, 7, 7),
    BitRate("ht_ds", 13000, 12700, 8, 8),
    BitRate("ht_ds", 26000, 24800, 9, 9),
    BitRate("ht_ds", 39000, 36600, 10, 10),
]

def ieee80211_to_idx(mbps):
    return [i for i, rate in enumerate(RATES)
            if rate.dot11_rate / 2 == mbps]


class EWMA:
    def __init__(self, time, time_step, pval):
        self.p = pval
        self.time = time
        self.step = time_step
        self.val = None

    def feed(self, time, val):
        if self.val is None:
            newval = val
        else:
            p = self.p
            newval = self.val * p + val * (1 - p)

        self.val = int(newval)
        self.time = time

    def read(self):
        if self.val:
            return self.val
        else: 
            return None
