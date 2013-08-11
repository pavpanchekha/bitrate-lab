import rates
import os
DEBUG = "DEBUG" in os.environ

NRATES = len(rates.RATES)

# The test harness uses a calculation of transmission time based on
# that in the SampleRate paper
BACKOFF = { "ofdm": [0], "ds": [0], "dsss": [0] }
for i in range(5, 11):
    BACKOFF["ds"].append(int(((2**i) - 1) * (20 / 2)))
for i in range(5, 11):
    BACKOFF["dsss"].append(int(((2**i) - 1) * (9 / 2)))
for i in range(4, 11):
    BACKOFF["ofdm"].append(int(((2**i) - 1) * (9 / 2)))

def backoff(rix, attempt):
    backoff_r = BACKOFF[rates.RATES[rix].phy]
    return backoff_r[min(attempt, len(backoff_r) - 1)] * 1000

def backoffs(rix):
    return len(BACKOFF[rates.RATES[rix].phy])

def difs(rix):
    version = "g" if rates.RATES[rix].phy == "ofdm" else "b"
    return (50 if version == "b" else 28) * 1000

def tx_lossless(rix, nbytes):
    # From the SampleRate paper.  See samplerate.py for annotated version.
    bitrate = rates.RATES[rix].mbps
    version = "g" if rates.RATES[rix].phy == "ofdm" else "b"
    sifs = 10 if version == "b" else 9
    ack = 304 # Somehow 6mb acks aren't used
    header = 192 if bitrate == 1 else 96 if version == "b" else 20

    return (sifs + ack + header + (nbytes * 8 / bitrate)) * 1000 # 1000 = us / ns

def tx_time(rix, prob, nbytes):
    txtime = tx_lossless(rix, nbytes)
    score = 0
    likeliness = 1

    if prob == 0: return float('inf')

    for i in range(0, backoffs(rix)):
        score += likeliness * prob * (txtime + difs(rix))
        txtime += txtime + backoff(rix, i + 1)
        likeliness *= (1 - prob)

    # backoff(rix, i) is now constant, so we are really summing
    #
    #     Sum[p (1 - p)^k (t + d + k (t + b)), {k, 0, Infinity}]
    #
    # where p is prob, d is difs(rix), b is backoff(rix, i), and
    # t is txtime_lossless

    # This can be summed by splitting (t + d + k (t + b)), yielding
    #
    #    (t + d) + (t + b) / p

    score += likeliness * ((txtime + difs(rix)) + \
                           (txtime + backoff(rix, i+1)) / prob)

    return score

class BitrateAlgorithm(object):
    class Rate(object):
        def __init__(self, alg, time, rix):
            self.alg = alg
            self.idx = rix
            self.info = rates.RATES[rix]
            self.mbps = self.info.mbps

        def __repr__(self):
            return "<Rate {}>".format(self.mbps)

    def __init__(self, time):
        self.start_time = time
        self.RATES = [self.Rate(self, time, rix)
                      for rix, _ in enumerate(rates.RATES)]

    def apply_rate(self, timestamp):
        return [(0, 1)]

    def process_feedback(self, status, timestamp, delay, tries):
        pass

def methods(cls):
    inst = [None]

    def initialize(time):
        inst[0] = cls(time)
    def apply_rate(time):
        assert inst[0], "Algorithm not properly initialized"
        return inst[0].apply_rate(time)
    def process_feedback(status, time, delay, tries):
        assert inst[0], "Algorithm not properly initialized"
        return inst[0].process_feedback(status, time, delay, tries)

    return initialize, apply_rate, process_feedback
