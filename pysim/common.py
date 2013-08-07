from __future__ import division
import collections
import math

BitRate = collections.namedtuple("BitRate", ["phy", "kbps", "user_kbps",
                                             "code", "dot11_rate"])

RATES = [
    BitRate("ds", 1000, 900, 0, 2),
    BitRate("ds", 2000, 1900, 1, 4),
    BitRate("dsss", 5500, 4900, 2, 11),
    BitRate("dsss", 11000, 8100, 3, 22),
    BitRate("ofdm", 6000, 5400, 4, 12),
    BitRate("ofdm", 9000, 7800, 5, 18),
    BitRate("ofdm", 12000, 10100, 6, 24),
    BitRate("ofdm", 18000, 14100, 7, 36),
    BitRate("ofdm", 24000, 17700, 8, 48),
    BitRate("ofdm", 36000, 23700, 9, 72),
    BitRate("ofdm", 48000, 27400, 10, 96),
    BitRate("ofdm", 54000, 30900, 11, 108),

    # Ignored but here for completeness
    #BitRate("ht_ss", 6500, 6400, 0, 0),
    #BitRate("ht_ss", 13000, 12700, 1, 1),
    #BitRate("ht_ss", 19500, 18800, 2, 2),
    #BitRate("ht_ss", 26000, 25000, 3, 3),
    #BitRate("ht_ss", 39000, 36700, 4, 4),
    #BitRate("ht_ss", 52000, 48100, 5, 5),
    #BitRate("ht_ss", 58500, 53500, 6, 6),
    #BitRate("ht_ss", 65000, 59000, 7, 7),
    #BitRate("ht_hgi", 72200, 65400, 7, 7),
    #BitRate("ht_ds", 13000, 12700, 8, 8),
    #BitRate("ht_ds", 26000, 24800, 9, 9),
    #BitRate("ht_ds", 39000, 36600, 10, 10),
]

def ieee80211_to_idx(mbps):
    opts = [i for i, rate in enumerate(RATES)
            if rate.dot11_rate == int(round(2 * mbps))]
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

# The average back-off period, in microseconds, for up to 7 attempts
# of a 802.11b unicast packet.

backoff = { "ofdm": [0], "ds": [0], "dsss": [0] }
for i in range(5, 11):
    backoff["ds"].append(int(((2**i) - 1) * (20 / 2)))
for i in range(5, 11):
    backoff["dsss"].append(int(((2**i) - 1) * (9 / 2)))
for i in range(4, 11):
    backoff["ofdm"].append(int(((2**i) - 1) * (9 / 2)))

def tx_time(rix, tries, nbytes):
    # From the SampleRate paper.  See samplerate.py for annotated version.
    bitrate = RATES[rix].dot11_rate / 2
    version = "g" if RATES[rix].phy == "ofdm" else "b"
    difs = 50 if version == "b" else 28
    sifs = 10 if version == "b" else 9
    ack = 304 # Somehow 6mb acks aren't used
    header = 192 if bitrate == 1 else 96 if version == "b" else 20
    
    assert tries > 0, "Cannot try a non-positive number of times"
    backoff_r = backoff[RATES[rix].phy][min(tries - 1, len(backoff) - 1)]

    us = difs + backoff_r + \
        tries * (sifs + ack + header + (nbytes * 8 / bitrate))
    return us * 1000

