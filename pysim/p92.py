from p92simple import P92Simple, ewma, EWMA_LEVEL
from constant import initialize
import bits

SR_LEVEL = .25

class P92(P92Simple):
    class Rate(P92Simple.Rate):
        def __init__(self, rix, info):
            P92Simple.Rate.__init__(self, rix, info)
            self.last_sortchange = None

        def init(self, time):
            P92Simple.Rate.init(self, time)
            self.last_sortchange = time

        def report_sortchange(self, time, pt, delta):
            if delta == 0:
                streaktime = time - self.last_sortchange
                if streaktime > self.samplerate:
                    self.samplerate = ewma(self.samplerate, streaktime, SR_LEVEL)
            else:
                if pt > 3: return
                streaktime = time - self.last_sortchange
                self.last_sortchange = time

                weight = SR_LEVEL ** (pt - abs(delta))
                self.samplerate = ewma(self.samplerate, streaktime/10, weight)

                #print self.mbps, ":", pt, "->", pt + delta, \
                #    ":", round(self.samplerate/1e9, 3), \
                #    "->", round(streaktime/10/1e9, 3)

            if self.samplerate > 1e9:
                self.samplerate = 1e9

        def report_actual(self, time, status):
            P92Simple.Rate.report_actual(self, time, status)
            self.samplerate = self.samplerate_normal

        def __repr__(self):
            return "<Rate {} p={:.3f} sr={:.3f}>".format(
                self.mbps, self.probability, self.samplerate/1e9)

    def process_feedback(self, status, timestamp, delay, tries):
        rix, _ = tries[0]
        rate = self.RATES[rix]

        oldpos = self.rates_sorted.index(rate)
        P92Simple.process_feedback(self, status, timestamp, delay, tries)
        newpos = self.rates_sorted.index(rate)

        change = newpos - oldpos
        rate.report_sortchange(timestamp, oldpos, change)
        #if change: print "    [0] = ", self.rates_sorted[0]

apply_rate, process_feedback = initialize(P92)
