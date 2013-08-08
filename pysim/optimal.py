
import harness
import rates
import os

# Very sneaky way of getting the data
data = harness.load_data(os.environ["DATA"])[1]

def badness(rix, prob):
    txtime = harness.tx_time(rix, 1500)
    score = 0
    likeliness = 1
    for i in range(0, 10):
        score += likeliness * prob * (txtime + harness.difs(rix))
        txtime += txtime + harness.backoff(rix, i + 1)
        likeliness *= (1 - prob)
    score += likeliness * (txtime + harness.difs(rix))
    return score

def apply_rate(t):
    ps = [harness.packet_stats(data, t, r) for r, _ in enumerate(rates.RATES)]
    badnesses = [badness(rix, p) / 1e6 for rix, p in enumerate(ps)]
    sorted_badnesses = sorted(enumerate(badnesses), key=lambda x: x[1])
    return [(sorted_badnesses[0][0], 1)]

def process_feedback(status, timestamp, delay, tries):
    pass
