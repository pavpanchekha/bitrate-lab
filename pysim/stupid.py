import os
from common import ieee80211_to_idx

FIXED_RATE = int(os.environ["RATE"]) if "RATE" in os.environ else 1
print("Running at rate %r Mbps...\n" % FIXED_RATE)

def apply_rate(time):
    try:
        r =  [(ieee80211_to_idx(FIXED_RATE)[0], 4)] * 4
        return r
    except:
        print ("%r Mbps is not an accepted rate. Your options are:\n"
               "1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54\n" % FIXED_RATE)
    
    exit()

def process_feedback(status, timestamp, delay, tries):
    pass
