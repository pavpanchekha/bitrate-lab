from constant import BitrateAlgorithm, initialize
import random
import bits

EWMA_LEVEL = .75
def ewma(old, new, weight):
    beta = EWMA_LEVEL / (1 - EWMA_LEVEL)
    return (old * beta + new * weight) / (beta + weight)

class P92Simple(BitrateAlgorithm):
    class Rate(BitrateAlgorithm.Rate):
        def __init__(self, rix, info):
            BitrateAlgorithm.Rate.__init__(self, rix, info)
            self.probability = 1.0
            self.confidence = 0
            self.samplerate = 1e8
            self.samplerate_normal = self.samplerate
            self.decayrate  = 5 * self.tx_time()
            
            # Time of next sample
            self.next_sample = None
            self.last_sample = None
            self.last_actual = None

        def init(self, time):
            self.last_sample = time
            self.last_actual = time
            self.recalc_next_sample(time)

        def report_sample(self, time, status):
            timespan = time - self.last_sample
            self.recalc_next_sample(time)
            self.last_sample = time

            #print self.mbps, self.confidence, status, round(self.probability, 2),
            self.confidence += 1
            self.probability = ewma(self.probability, 1.0 if status else 0.0,
                                    timespan / self.samplerate_normal * \
                                    1000 / min(self.confidence, 1000))
            #print round(self.probability, 2)

            self.recalc_decay()

        def report_actual(self, time, status):
            timespan = time - self.last_actual
            self.probability = ewma(self.probability, 1 if status else 0,
                                    timespan / self.decayrate * \
                                    1000 / min(self.confidence + 1, 1000))
            self.last_actual = time
            self.recalc_decay()

        def recalc_decay(self):
            self.decay_rate = 5 * self.tx_time()

        def recalc_next_sample(self, time):
            self.next_sample = time + (random.random() + .5) * self.samplerate

        def tx_lossless(self, nbytes=1500):
            return bits.tx_lossless(self.idx, nbytes)

        def tx_time(self, nbytes=1500):
            return bits.tx_time(self.idx, self.probability, nbytes)

        def __repr__(self):
            return "<Rate {} p={:.3f}>".format(self.mbps, self.probability)

    def __init__(self):
        BitrateAlgorithm.__init__(self)
        self.was_sample = False
        self.inited = False
        self.rates_sorted = list(reversed(self.RATES))


    def apply_rate(self, timestamp):
        if not self.inited:
            for r in self.RATES: r.init(timestamp)
            self.inited = True
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
            rate.report_actual(timestamp, status)

        self.rates_sorted.sort(key=self.Rate.tx_time)

apply_rate, process_feedback = initialize(P92Simple)
