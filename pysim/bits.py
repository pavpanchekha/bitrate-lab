import rates
import os
DEBUG = "DEBUG" in os.environ

NRATES = len(rates.RATES)

# The test harness uses a calculation of transmission time based on
# that in the SampleRate paper
BACKOFF = { "ofdm": [0], "ds": [0], "dsss": [0] }
for i in range(5, 11):
    BACKOFF["ds"].append(int(((2**i) - 1) * (20 / 2)))
for i in range(5, 11):
    BACKOFF["dsss"].append(int(((2**i) - 1) * (9 / 2)))
for i in range(4, 11):
    BACKOFF["ofdm"].append(int(((2**i) - 1) * (9 / 2)))

def backoff(rix, attempt):
    return BACKOFF[rates.RATES[rix].phy][min(attempt, len(BACKOFF) - 1)] * 1000

def difs(rix):
    version = "g" if rates.RATES[rix].phy == "ofdm" else "b"
    return (50 if version == "b" else 28) * 1000

def tx_lossless(rix, nbytes):
    # From the SampleRate paper.  See samplerate.py for annotated version.
    bitrate = rates.RATES[rix].mbps
    version = "g" if rates.RATES[rix].phy == "ofdm" else "b"
    sifs = 10 if version == "b" else 9
    ack = 304 # Somehow 6mb acks aren't used
    header = 192 if bitrate == 1 else 96 if version == "b" else 20

    return (sifs + ack + header + (nbytes * 8 / bitrate)) * 1000 # 1000 = us / ns

def tx_time(rix, prob, nbytes):
    txtime = tx_lossless(rix, nbytes)
    score = 0
    likeliness = 1
    for i in range(0, 10):
        score += likeliness * prob * (txtime + difs(rix))
        txtime += txtime + backoff(rix, i + 1)
        likeliness *= (1 - prob)
    score += likeliness * (txtime + difs(rix))
    return score
