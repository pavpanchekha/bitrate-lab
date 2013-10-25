import random
import bits

class Louis(bits.BitrateAlgorithm):
    # The weighting for old data in the EWMA algorithm; equal to level of 75%
    EWMA_BETA = 3
    # The fixed-point arithmetic shift
    SCALE = 16
    # How frequently to sample "normally"; from Minstrel
    SAMPLE_NORMAL = .3e9 # Every .3 seconds
    # A multiplier for weighing normal packets.
    # Relatively little effect on performance.
    NORMAL_DECAY = 10
    # How large packets are expected to be
    NBYTES = 1200

    def FRAC(self, val, div):
        return (val << self.SCALE) // div

    def TRUNC(self, val):
        return val >> self.SCALE

    class Rate(bits.BitrateAlgorithm.Rate):
        def __init__(self, alg, time, rix):
            bits.BitrateAlgorithm.Rate.__init__(self, alg, time, rix)
            self.probability = 1 << self.alg.SCALE

            self.samplerate = alg.SAMPLE_NORMAL
            self.normalrate = alg.NORMAL_DECAY * self.tx_time()
            
            # Time of next sample
            self.next_sample = time
            self.last_sample = time
            self.last_actual = time
            self.recalc_next_sample(time)

        def ewma(self, old, new, weight):
            beta = self.alg.EWMA_BETA * 256
            return (old * beta + new * weight) // (beta + weight)

        def report_sample(self, time, status):
            timespan = time - self.last_sample
            scale = 1 << self.alg.SCALE
            self.probability = self.ewma(self.probability,
                                         scale if status else 0,
                                         (256 * timespan) // self.alg.SAMPLE_NORMAL)

            self.last_sample = time
            self.recalc_next_sample(time)

        def report_normal(self, time, status):
            timespan = time - self.last_actual
            scale = 1 << self.alg.SCALE
            self.probability = self.ewma(self.probability,
                                         scale if status else 0,
                                         (256 * timespan) // self.normalrate)
            self.last_actual = time

        def tx_time(self):
            prob = self.probability / (1 << self.alg.SCALE)
            return bits.tx_time(self.idx, prob, self.alg.NBYTES)

        def recalc_next_sample(self, time):
            self.next_sample = int(time + (random.random() + .5) * self.samplerate)

        def __repr__(self):
            return "<Rate {} p={:.3f}>".format(self.mbps, self.probability)

    def __init__(self, time):
        bits.BitrateAlgorithm.__init__(self, time)
        self.was_sample = False
        self.rates_sorted = list(reversed(self.RATES))

    def apply_rate(self, timestamp):
        samplable_rates = [rate for rate in self.RATES
                           if rate.next_sample is None
                           or rate.next_sample < timestamp]

        if samplable_rates:
            self.was_sample = True
            rate = random.choice(samplable_rates)
        else:
            self.was_sample = False
            rate = self.rates_sorted[0]

        return [(rate.idx, 1)]

    def process_feedback(self, status, timestamp, delay, tries):
        rix, _ = tries[0]
        rate = self.RATES[rix]

        if self.was_sample:
            rate.report_sample(timestamp, status)
        else:
            rate.report_normal(timestamp, status)

        self.rates_sorted.sort(key=self.Rate.tx_time)

class Armstrong(Louis):
    # Max length of time between samples; from Minstrel
    SAMPLE_MAX = 2e9
    # Normal sampling rate decreased, since it will auto-adjust upwards
    SAMPLE_NORMAL = .01e9 # Approximately the maximum sampling rate
    # What position in the sorted bitrates should have sampling rate
    # equal reorder rate?
    SORTORDER_EVEN = 4
    # How much (multiplicatively) each step in sort order should
    # change things.
    SORTORDER_STEP = 1.414

    class Rate(Louis.Rate):
        def __init__(self, alg, time, rix):
            Louis.Rate.__init__(self, alg, time, rix)
            self.last_sortchange = time

        def report_sortchange(self, time, pt, delta):
            streaktime = time - self.last_sortchange
            multiply = self.alg.SORTORDER_STEP ** (pt - self.alg.SORTORDER_EVEN)

            if delta == 0 and streaktime > self.samplerate:
                self.samplerate = self.ewma(self.samplerate, multiply * streaktime, 256)
            elif delta == 0:
                return
            else:
                self.last_sortchange = time
                self.samplerate = self.ewma(self.samplerate, multiply * streaktime, 256)

            if self.samplerate > self.alg.SAMPLE_MAX:
                self.samplerate = self.alg.SAMPLE_MAX

        def report_normal(self, time, status):
            Louis.Rate.report_normal(self, time, status)
            self.samplerate = self.alg.SAMPLE_NORMAL

        def __repr__(self):
            return "<Rate {} p={:.3f} sr={:.3f}>".format(
                self.mbps, self.probability, self.samplerate/1e9)

    def process_feedback(self, status, timestamp, delay, tries):
        rix, _ = tries[0]
        rate = self.RATES[rix]

        oldpos = self.rates_sorted.index(rate)
        Louis.process_feedback(self, status, timestamp, delay, tries)
        newpos = self.rates_sorted.index(rate)

        change = newpos - oldpos
        rate.report_sortchange(timestamp, oldpos, change)

initialize, apply_rate, process_feedback = bits.methods(Armstrong)
