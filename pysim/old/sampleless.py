import rates
import math
import random

BLOCK_DURATION = 100e6 # 100e6 = 100ms
PROB_SAMPLE = .1

class Rate(object):
    def __init__(self, idx):
        self.idx = idx
        self.info = rates.RATES[idx]
        self.rate = self.info.mbps
        self.ewma = rates.BalancedEWMA(0.0, BLOCK_DURATION, 0.75)
        self.block = [ 0 , 0 ] # Successes , Failures
    
    def txtime_perfect(self, length=1200):
        return rates.tx_time(self.idx, length)
    
    def txtime(self, prob=None, length=1200):
        if prob is None: prob = self.prob()
        if prob == 0:
            return float('inf')
        else:
            return rates.tx_time(self.idx, length) / prob

    def prob(self):
        prob = self.ewma.read()
        if prob is None:
            return 1
        return prob / 18000 

    def sampleboon(self):
        return 1 / self.txtime(self.prob() * .99 + .01)

class SampleLess(object):
    def __init__(self):
        self.rates = [Rate(i) for i in range(len(rates.RATES))]
        self.block_start = None
        self.packets = 0
        self.samples = 0

    def apply_rate(self, timestamp):
        # Set the block timer
        if self.block_start is None:
            self.block_start = timestamp

        if self.samples / PROB_SAMPLE <= self.packets:
            rate = self.sample_rate()
            self.samples += 1
        else:
            rate = self.normal_rate()

        self.packets += 1

        return [(rate.idx, 1)]

    def normal_rate(self):
        return min(self.rates, key=Rate.txtime)

    def sample_rate(self):
        benefit = list(map(Rate.sampleboon, self.rates))
        total = sum(benefit)
        rand = random.random() * total
        #print
        #print "DEBUG", rand, total, benefit,

        rate = None
        for b, rate in zip(benefit, self.rates):
            rand -= b
            if rand < 0:
                break

        if not rate:
            rate = random.choice(self.rates)
        #print rate.rate

        return rate

    def process_feedback(self, status, timestamp, delay, tries):
        # This loops is explicit because the last element is strange
        for i in range(len(tries) - 1):
            rate, retries = tries[i]
            self.process_failure(self.rates[rate], retries)

        rate, retries = tries[-1]
        if status:
            self.process_failure(self.rates[rate], retries - 1)
            self.process_success(self.rates[rate], 1)
        else:
            self.process_failure(self.rates[rate], retries)

        if timestamp - self.block_start > BLOCK_DURATION:
            self.block_start = None
            self.feed_block(timestamp)

    def process_success(self, rate, num):
        rate.block[0] += num

    def process_failure(self, rate, num):
        rate.block[1] += num
    
    def feed_block(self, timestamp):
        for r in self.rates:
            succ, fail = r.block
            r.block = [0, 0]
            if succ or fail:
                r.ewma.feed(timestamp, succ, succ + fail)

alg = SampleLess()
apply_rate = alg.apply_rate
process_feedback = alg.process_feedback
