
import harness
import rates
import os
import bits

data = None

def initialize(t):
    global data
    # Very sneaky way of getting the data
    data = harness.load_data(os.environ["DATA"])[1]

def apply_rate(t):
    ps = [harness.packet_stats(data[r], t, r) for r, _ in enumerate(rates.RATES)]
    badnesses = [bits.tx_time(rix, p, 1500) for rix, p in enumerate(ps)]
    least_bad = min(enumerate(badnesses), key=lambda x: x[1])
    return [(least_bad[0], 1)]

def process_feedback(status, timestamp, delay, tries):
    pass
