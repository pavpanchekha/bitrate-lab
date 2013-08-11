import bits
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

class Constant(bits.BitrateAlgorithm):
    def apply_rate(self, timestamp):
        return [(IDX, 1)]

initialize, apply_rate, process_feedback = bits.methods(Constant)
