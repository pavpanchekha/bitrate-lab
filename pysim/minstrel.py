# This module implements the Minstrel rate control algorithm based on
# the 3.10.5 Linux kernel. We assume multi-rate retry capabilities, so
# we omit code for the non-MRR case.

from __future__ import division

import random
import rates
import math
from collections import namedtuple

packet_count = 0
sample_count = 0
sample_deferred = 0

time_last_called = 0
probeFlag = False

MAX_RETRY = 7
SAMPLING_RATIO = 10
MINSTREL_SCALE = 16
EWMA_LEVEL = 96
EWMA_DIV = 128

def MINSTREL_FRAC(val, div):
    return (val << MINSTREL_SCALE) // div

def MINSTREL_TRUNC(val):
    return val >> MINSTREL_SCALE

def tx_time(rate, length=1200): #rix is index to RATES, length in bytes
    # Adapted from 802.11 util.c ieee80211_frame_duration()

    #"calculate duration (in microseconds, rounded up to next higher
    # integer if it includes a fractional microsecond) to send frame of
    # len bytes (does not include FCS) at the given rate. Duration will
    # also include SIFS."

    rateinfo = rate.info

    if rateinfo.phy == "ofdm":
        #"OFDM:
        # N_DBPS = DATARATE x 4
        # N_SYM = Ceiling((16+8xLENGTH+6) / N_DBPS)
        # (16 = SIGNAL time, 6 = tail bits)
        # TXTIME = T_PREAMBLE + T_SIGNAL + T_SYM x N_SYM + Signal Ext

        # T_SYM = 4 usec
        # 802.11a - 17.5.2: aSIFSTime = 16 usec
        # 802.11g - 19.8.4: aSIFSTime = 10 usec + signal ext = 6 usec"
        dur = 16 # SIFS + signal ext */
        dur += 16 # 17.3.2.3: T_PREAMBLE = 16 usec */
        dur += 4 # 17.3.2.3: T_SIGNAL = 4 usec */
        dur += 4 * (math.ceil((16+8*(length+4)+6)/(4*rateinfo.mbps))+1) # T_SYM x N_SYM

    else:
        #"802.11b or 802.11g with 802.11b compatibility:
        # 18.3.4: TXTIME = PreambleLength + PLCPHeaderTime +
        # Ceiling(((LENGTH+PBCC)x8)/DATARATE). PBCC=0.

        # 802.11 (DS): 15.3.3, 802.11b: 18.3.4
        # aSIFSTime = 10 usec
        # aPreambleLength = 144 usec or 72 usec with short preamble
        # aPLCPHeaderLength = 48 usec or 24 usec with short preamble"
        dur = 10 # aSIFSTime = 10 usec
        dur += (72 + 24) #using short preamble, otw we'd use (144 + 48)
        dur += math.ceil((8*(length + 4))/rateinfo.mbps)+1

    return dur

class Rate:
    def __init__(self, rix):
        self.idx = rix
        self.info = rates.RATES[rix]
        self.rate = self.info.mbps
        self.throughput = 0 #in bits per second
        self.last_update = 0.0 #timestamp of last update, ns(?)
        self.probability = 0
        self.success = 0  #number of successful xmissions in cur time interval
        self.attempts = 0 #number of attempted transmissions in cur time interval
        self.losslessTX = tx_time(self, 1200) #microseconds, pktsize 1200 in kernel,
        self.ack = tx_time(self, 10) #microseconds, assumes 1mbps ack rate

        self.sample_skipped = 0

        #what is the difference between these?
        self.sample_limit = -1
        self.retry_count = 1

        #a complicated loop to calculate the initial adjusted retry count
        tx_time_ = self.losslessTX + self.ack#includes ack
        condition = True
        while condition:
            #add one retransmission
            tx_time_single = self.ack + self.losslessTX

            #contention window
            cw = 15 # 15 = CWmin
            tx_time_single += (9* cw) >> 1;
            cw = min((cw << 1) | 1, 1023) # 1023 = CWmax

            tx_time_ += tx_time_single

            self.retry_count += 1
            # 6000 == segment size
            condition = (tx_time_ < 6000) and (self.retry_count < MAX_RETRY)

        self.adjusted_retry_count = self.retry_count #Max retrans. used for probing

    def ewma(self, new, weight):
        old = self.probability
        self.probability = (new * (EWMA_DIV - weight) + old * weight) // EWMA_DIV;

# The modulation scheme used in 802.11g is orthogonal
# frequency-division multiplexing (OFDM)copied from 802.11a with data
# rates of 6, 9, 12, 18, 24, 36, 48, and 54 Mbit/s, and reverts to CCK
# (like the 802.11b standard) for 5.5 and 11 Mbit/s and DBPSK/DQPSK+#
# DSSS for 1 and 2 Mbit/s. Even though 802.11g operates in the same
# frequency band as 8# 02.11b, it can achieve higher data rates
# because of its heritage to 802.11a.
#RATES = dict((r, Rate(r)) for r in [1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])
RATES = [Rate(rix) for rix in range(len(rates.RATES))]

# Chosen rates
rate_struct = namedtuple("Rates", ["best", "next", "prob", "base"])
choices = rate_struct(RATES[11], RATES[10], RATES[1], RATES[0])

#"10 times a second (this frequency is alterable by changing the
# driver code) a timer fires, which evaluates the statistics
# table. EWMA calculations (described below) are used to process the
# success history of each rate. On completion of the calculation, a
# decision is made as to the rate which has the best throughput,
# second best throughput, and highest probability of success. This
# data is used for populating the retry chain during the next 100
# ms. Note that the retry chain is described below."
def apply_rate(cur_time):
    global packet_count, sample_count, sample_deferred, time_last_called

    if cur_time - time_last_called >= 1e8:
        update_stats(cur_time)
        time_last_called = cur_time

    #"Minstrel spends a particular percentage of frames, doing "look
    # around" i.e.  randomly trying other rates, to gather
    # statistics. The percentage of "look around" frames defaults to
    # 10%. The distribution of lookaround frames is also randomized
    # somewhat to avoid any potential "strobing" of lookaround between
    # similar nodes."

    # Try |         Lookaround rate              | Normal rate
    #     | random < best    | random > best     |
    # --------------------------------------------------------------
    #  1  | Best throughput  | Random rate       | Best throughput
    #  2  | Random rate      | Best throughput   | Next best throughput
    #  3  | Best probability | Best probability  | Best probability
    #  4  | Lowest Baserate  | Lowest baserate   | Lowest baserate

    delta = (packet_count * SAMPLING_RATIO // 100) - \
            (sample_count + sample_deferred // 2)

    if delta > 0: # In this case we attempt to sample a rate
        #"Analysis of information showed that the system was sampling
        # too hard at some rates. For those rates that never work
        # (54mb, 500m range) there is no point in sending 10 sample
        # packets (< 6 ms time). Consequently, for the very very low
        # probability rates, we sample at most twice."

        if packet_count >= 10000:
            sample_count = 0
            packet_count = 0
            sample_deferred = 0
        elif delta > len(RATES) * 2:
            #"With multi-rate retry, not every planned sample
            # attempt actually gets used, due to the way the retry
            # chain is set up - [max_tp,sample,prob,lowest] for
            # sample_rate < max_tp.
            #
            # If there's too much sampling backlog and the link
            # starts getting worse, minstrel would start bursting
            # out lots of sampling frames, which would result
            # in a large throughput loss."
            sample_count += delta  - (len(RATES)*2)

        # The kernel actually doesn't use a random number generator
        # here, instead using a pregenerated table of "random" numbers.
        # See net/mac80211/rc80211_minstrel.c :: init_sample_table

        # TODO: Use the mechanism the kernel uses
        randrate = random.choice(RATES)

	#"Decide if direct ( 1st mrr stage) or indirect (2nd mrr
	# stage) rate sampling method should be used.  Respect such
	# rates that are not sampled for 20 interations."

        if randrate.rate < choices.best.rate and \
           randrate.sample_skipped < 20:
            #"Only use IEEE80211_TX_CTL_RATE_CTRL_PROBE to mark
            # packets that have the sampling rate deferred to the
            # second MRR stage. Increase the sample counter only if
            # the deferred sample rate was actually used.  Use the
            # sample_deferred counter to make sure that the sampling
            # is not done in large bursts"
            probe_flag = True
            sample_deferred += 1

            chain = [choices.best, randrate, choices.prob, choices.base]
        else:
            if randrate.sample_limit != 0:
                sample_count += 1
                if randrate.sample_limit > 0:
                    randrate.sample_limit -= 1

            chain = [randrate, choices.best, choices.prob, choices.base]

    else:
        chain = [choices.best, choices.next, choices.prob, choices.base]

    mrr = [(rate.idx, rate.adjusted_retry_count) for rate in chain]

    return mrr

def process_feedback(status, timestamp, delay, tries):
    global packet_count, probeFlag, time_last_called, sample_deferred, sample_count
    for t in range(len(tries)):
        (rix, br_tries) = tries[t]

        if br_tries > 0:
            br = RATES[rix]
            br.attempts = (br.attempts + br_tries)
            packet_count += br_tries

            #if the packet was successful...
            if status and t == (len(tries)-1):
                br.success += 1

    #if we had the random rate second in the retry chain, and actually ended up
    #using it, increment the count and unset the flag
    if t > 1 and probeFlag:
        sample_count += 1
        probeFlag = False

    if sample_deferred > 0:
        sample_deferred -= 1

    if timestamp - time_last_called >= 1e8:
        update_stats(timestamp)


def update_stats(timestamp):
    global choices

    for br in RATES:
        usecs = tx_time(br)

        if br.attempts: # The kernel wraps this check in an unlikely()
            br.sample_skipped = 0
            p = MINSTREL_FRAC(br.success, br.attempts)
            br.ewma(p, EWMA_LEVEL)
        else:
            br.sample_skipped += 1

        br.success = 0
        br.attempts = 0

        if (br.probability < MINSTREL_FRAC(10, 100)):
            br.throughput = 0
        else:
            br.throughput = br.probability * (1000000 // usecs)

        #"Sample less often below the 10% chance of success.
        # Sample less often above the 95% chance of success."
        if br.probability > MINSTREL_FRAC(95, 100) or \
           br.probability < MINSTREL_FRAC(10, 100):
            br.adjusted_retry_count = br.retry_count >> 1
            if br.adjusted_retry_count > 2:
                br.adjusted_retry_count = 2
            br.sample_limit = 4
        else:
            br.sample_limit = -1
            br.adjusted_retry_count = br.retry_count

        if not br.adjusted_retry_count:
            br.adjusted_retry_count = 2

    br.last_update = timestamp

    #changed rates to rates_, changed rates to rates.values() -CJ
    rates_by_tp = sorted(RATES, key=lambda br: br.throughput, reverse=True)
    bestThruput = rates_by_tp[0]
    nextThruput = rates_by_tp[1]

    #"To determine the most robust rate (max_prob_rate) used at 3rd
    # mmr stage we distinct between two cases:
    # (1) if any success probabilitiy >= 95%, out of those rates
    # choose the maximum throughput rate as max_prob_rate
    # (2) if all success probabilities < 95%, the rate with highest
    # success probability is choosen as max_prob_rate"

    if any(br.probability > MINSTREL_FRAC(95, 100) for br in RATES):
        good_rates = [br for br in RATES
                      if br.probability > MINSTREL_FRAC(95, 100)]
        bestProb = max(good_rates, key=lambda br: br.throughput)
    else:
        bestProb = max(RATES, key=lambda br: br.probability)

    choices = rate_struct(bestThruput, nextThruput, bestProb, choices.base)

def initialize(time):
    pass
