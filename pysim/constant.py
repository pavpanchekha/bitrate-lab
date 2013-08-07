import os
import common

RATE=float(os.environ["RATE"]) if "RATE" in os.environ else 1

# Read the rate as a Mbps value and convert it to an index
try:
    IDX = common.ieee80211_to_idx(RATE)
except ValueError:
    opts = [str(rate.dot11_rate) for rate in common.RATES]
    print("Invalid rate.  Options are: {}".format(", ".join(opts)))
    exit()
else:
    print("Running at rate %r Mbps..." % RATE)

def apply_rate(time):
    return [(IDX, 4)] * 4

def process_feedback(status, timestamp, delay, tries):
    pass
