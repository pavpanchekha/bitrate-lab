import rates
import os

RATE=float(os.environ["RATE"]) if "RATE" in os.environ else 1

# Read the rate as a Mbps value and convert it to an index
try:
    IDX = [i for i, r in enumerate(rates.RATES) if r.mbps == RATE][0]
except IndexError:
    opts = [str(rate.mbps) for rate in rates.RATES]
    print("Invalid rate.  Options are: {}".format(", ".join(opts)))
    exit()
else:
    print("Running at rate %r Mbps..." % RATE)

class BitrateAlgorithm(object):
    class Rate(object):
        def __init__(self, rix, info):
            self.idx = rix
            self.info = info
            self.mbps = info.mbps

        def __repr__(self):
            return "<Rate {}>".format(self.mbps)

    def __init__(self):
        self.RATES = [self.Rate(rix, info) for rix, info in enumerate(rates.RATES)]

    def apply_rate(self, timestamp):
        return [(IDX, 1)]

    def process_feedback(self, status, timestamp, delay, tries):
        pass

def initialize(cls):
    inst = cls()
    return inst.apply_rate, inst.process_feedback

apply_rate, process_feedback = initialize(BitrateAlgorithm)
