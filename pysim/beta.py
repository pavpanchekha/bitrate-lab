from alpha import Alpha, ewma, EWMA_LEVEL
from constant import initialize
import bits

SR_LEVEL = .9

class Beta(Alpha):
    class Rate(Alpha.Rate):
        def __init__(self, rix, info):
            Alpha.Rate.__init__(self, rix, info)
            self.last_sortchange = None

        def init(self, time):
            Alpha.Rate.init(self, time)
            self.last_sortchange = time

        def report_sortchange(self, time, pt, delta):
            if delta == 0:
                streaktime = time - self.last_sortchange
                if streaktime > self.samplerate:
                    self.samplerate = ewma(self.samplerate, streaktime, .1)
            else:
                streaktime = time - self.last_sortchange
                self.last_sortchange = time

                weight = SR_LEVEL ** (pt - abs(delta))
                self.samplerate = ewma(self.samplerate, streaktime/10, weight)

                #print self.mbps, ":", pt, "->", pt + delta, ":", round(self.samplerate/1e9, 3), "->", round(streaktime/10/1e9, 3)

            if self.samplerate > 1e9:
                self.samplerate = 1e9

        def __repr__(self):
            return "<Rate {} p={:.3f} sr={:.3f}>".format(
                self.mbps, self.probability, self.samplerate/1e9)

    def process_feedback(self, status, timestamp, delay, tries):
        rix, _ = tries[0]
        rate = self.RATES[rix]

        oldpos = self.rates_sorted.index(rate)
        Alpha.process_feedback(self, status, timestamp, delay, tries)
        newpos = self.rates_sorted.index(rate)

        change = newpos - oldpos
        rate.report_sortchange(timestamp, oldpos, change)
        #if change: print "    [0] = ", self.rates_sorted[0]

apply_rate, process_feedback = initialize(Beta)
