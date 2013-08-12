import random
import bits

class Louis(bits.BitrateAlgorithm):
    # The weighting for old data in the EWMA algorithm; from Minstrel
    EWMA_LEVEL = .75
    # How frequently to sample "normally"; from Minstrel
    SAMPLE_NORMAL = .3e9 # Every .3 seconds
    # A multiplier for weighing normal packets.
    # Relatively little effect on performance.
    NORMAL_DECAY = 10
    # How large packets are expected to be
    NBYTES = 1500

    class Rate(bits.BitrateAlgorithm.Rate):
        def __init__(self, alg, time, rix):
            bits.BitrateAlgorithm.Rate.__init__(self, alg, time, rix)
            self.probability = 1.0

            self.samplerate = alg.SAMPLE_NORMAL
            self.normalrate = alg.NORMAL_DECAY * self.tx_time()
            
            # Time of next sample
            self.next_sample = time
            self.last_sample = time
            self.last_actual = time
            self.recalc_next_sample(time)

        def ewma(self, old, new, weight):
            beta = self.alg.EWMA_LEVEL / (1 - self.alg.EWMA_LEVEL)
            return (old * beta + new * weight) / (beta + weight)

        def report_sample(self, time, status):
            timespan = time - self.last_sample
            self.probability = self.ewma(self.probability, 1 if status else 0,
                                         timespan / self.alg.SAMPLE_NORMAL)

            self.last_sample = time
            self.recalc_next_sample(time)

        def report_normal(self, time, status):
            timespan = time - self.last_actual
            self.probability = self.ewma(self.probability, 1 if status else 0,
                                         timespan / self.normalrate)
            self.last_actual = time

        def tx_time(self):
            return bits.tx_time(self.idx, self.probability, self.alg.NBYTES)

        def recalc_normalrate(self):
            self.normalrate = self.alg.NORMAL_DECAY * self.tx_time()

        def recalc_next_sample(self, time):
            self.next_sample = time + (random.random() + .5) * self.samplerate

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
    # What position in the sorted bitrates past which to ignore sortorder changes
    SORTORDER_CUTOFF = 4

    class Rate(Louis.Rate):
        def __init__(self, alg, time, rix):
            Louis.Rate.__init__(self, alg, time, rix)
            self.last_sortchange = time

        def report_sortchange(self, time, pt, delta):
            streaktime = time - self.last_sortchange

            if delta == 0 and streaktime > self.samplerate:
                self.samplerate = self.ewma(self.samplerate, streaktime, 1)
            elif delta == 0:
                return
            elif pt < self.alg.SORTORDER_CUTOFF
                self.last_sortchange = time
                self.samplerate = self.ewma(self.samplerate, streaktime/10, 1)

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
