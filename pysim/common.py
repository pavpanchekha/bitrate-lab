from __future__ import division
import collections
import math

BitRate = collections.namedtuple("BitRate", ["phy", "kbps", "user_kbps",
                                             "code", "dot11_rate"])

# The 802.11, 802.11b, and 802.11g rates
RATES = [
    BitRate("ds",    1000,   900,  0, 1.0),
    BitRate("ds",    2000,  1900,  1, 2.0),
    BitRate("dsss",  5500,  4900,  2, 5.5),
    BitRate("dsss", 11000,  8100,  3, 11.0),
    BitRate("ofdm",  6000,  5400,  4, 6.0),
    BitRate("ofdm",  9000,  7800,  5, 9.0),
    BitRate("ofdm", 12000, 10100,  6, 12.0),
    BitRate("ofdm", 18000, 14100,  7, 18.0),
    BitRate("ofdm", 24000, 17700,  8, 24.0),
    BitRate("ofdm", 36000, 23700,  9, 36.0),
    BitRate("ofdm", 48000, 27400, 10, 48.0),
    BitRate("ofdm", 54000, 30900, 11, 54.0),
]

def ieee80211_to_idx(mbps):
    opts = [i for i, rate in enumerate(RATES) if rate.dot11_rate == mbps]
    if opts:
        return opts[0]
    else:
        raise ValueError("No bitrate with throughput {} Mbps exists".format(mbps))


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
        if self.val is not None:
            return self.val
        else: 
            return None

class BalancedEWMA:
    def __init__(self, time, time_step, pval):
        self.p = pval
        self.time = time
        self.step = time_step

        self.blocks = 0
        self.denom = 0
        self.val = None

    def feed(self, time, num, denom):
        if self.blocks == 0:
            self.denom = denom
            newval = num / denom
        else:
            avg_block = self.denom / self.blocks
            block_weight = denom / avg_block
            relweight = self.p / (1 - self.p)

            prob = num / denom

            newval = (self.val * relweight + prob * block_weight) / \
                     (relweight + block_weight)

        self.blocks += 1
        self.val = newval
        self.time = time

    def read(self):
        if self.val is not None:
            return int(self.val * 18000)
        else:
            return None
