import random
import bits

class Base(bits.BitrateAlgorithm):
    EWMA_LEVEL = .75
    SAMPLE_NORMAL = .1e9 # Every .1 seconds
    START_PROBABILITY = 1.0
    NORMAL_DECAY = 5
    NBYTES = 1500

    class Rate(bits.BitrateAlgorithm.Rate):
        def __init__(self, alg, time, rix):
            bits.BitrateAlgorithm.Rate.__init__(self, alg, time, rix)
            self.probability = self.alg.START_PROBABILITY

            self.samplerate = alg.SAMPLE_NORMAL
            self.recalc_normalrate()
            
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
            self.probability = self.ewma(self.probability, 1.0 if status else 0.0,
                                         timespan / self.alg.SAMPLE_NORMAL)

            self.last_sample = time
            self.recalc_next_sample(time)
            self.recalc_normalrate()

        def report_normal(self, time, status):
            timespan = time - self.last_actual
            self.probability = self.ewma(self.probability, 1 if status else 0,
                                         timespan / self.normalrate)
            self.last_actual = time
            self.recalc_normalrate()

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

Louis = Base

class Armstrong(Louis):
    SR_LEVEL = .25

    class Rate(Louis.Rate):
        def __init__(self, alg, time, rix):
            Louis.Rate.__init__(self, alg, time, rix)
            self.last_sortchange = time

        def report_sortchange(self, time, pt, delta):
            if delta == 0:
                streaktime = time - self.last_sortchange
                if streaktime > self.samplerate:
                    self.samplerate = self.ewma(self.samplerate, streaktime,
                                                self.alg.SR_LEVEL)
            else:
                if pt > 3: return
                streaktime = time - self.last_sortchange
                self.last_sortchange = time

                weight = self.alg.SR_LEVEL ** (pt - abs(delta))
                self.samplerate = self.ewma(self.samplerate, streaktime/10, weight)

            if self.samplerate > 1e9:
                self.samplerate = 1e9

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
