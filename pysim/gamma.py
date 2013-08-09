from beta import Beta
from constant import initialize
import bits
import random

PHASE_SAMPLE = 1e8
PHASE_STEADY = 1e9
STEADY_SAMPLECOUNT = 5

class Gamma(Beta):
    def __init__(self):
        Beta.__init__(self)
        self.start_time = None
        self.nonrandom = 0 # Index for cycling

    def apply_rate(self, time):
        if not self.inited:
            self.start_time = time
        suggestion = Beta.apply_rate(self, time)

        if time - self.start_time < PHASE_SAMPLE:
            rate = self.RATES[self.nonrandom]
            self.nonrandom = (self.nonrandom + 1) % bits.NRATES
        elif time - self.start_time < PHASE_STEADY:
            rate = max(self.RATES, key=lambda r: r.probability)
        else:
            return suggestion

        rate.recalc_next_sample(time)
        return [(rate.idx, 1)]

apply_rate, process_feedback = initialize(Gamma)
