import os
import common

RATE=float(os.environ["RATE"]) if "RATE" in os.environ else 1

opts = common.ieee80211_to_idx(RATE)
if opts:
    FIXED_RATE = opts[0]
    print("Running at rate %r Mbps..." % RATE)
else:
    print("Invalid rate.  Options are: {}".format(", ".join(str(rate.dot11_rate / 2) for rate in common.RATES)))
    exit()

def apply_rate(time):
    return [(FIXED_RATE, 4)] * 4

def process_feedback(status, timestamp, delay, tries):
    pass
