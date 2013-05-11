import numpy
import time
import common
import os, sys
import random

DEBUG = "DEBUG" in os.environ

def load_data(source):
    return numpy.load(source) / 1. # Convert to float

def packet_stats(data, time, rate):
    time = time % len(data)
    
    # First, we try to find a prior instance of such transmission
    for i in range(time, -1, -1):
        if data[i, rate].any():
            delay, tries = data[i, rate]
            return (delay, tries)

    # Next, try to find a future instance
    for i in range(len(data)-1, time, -1):
        if data[i, rate].any():
            delay, tries = data[i, rate]
            return (delay, tries)
    
    # Otherwise, this seems like a big problem, so we cause an error
    raise ValueError("No data available at bit-rate", rate)

def baseline(data):
    s = data.sum(0)[0]
    return s[0] / s[1]

class Harness:
    def __init__(self, data, choose_rate, push_statistics):
        # Keep the time somewhat believable
        #self.clock = time.time()
        self.clock = 0
        self.packet_num = 0
        self.baseline = baseline(data)
        self.choose_rate = choose_rate
        self.push_statistics = push_statistics

        self.histogram = [0] * len(common.RATES)

    def send_packet(self):
        rate_arr = self.choose_rate(self.clock)

        if DEBUG:
            print("Sending packet at:", end=" ")
            for (rate, tries) in rate_arr:
                print("Rate {}/{}".format(rate, tries), end=" ")
            print()

        tot_delay = 0
        tot_tries = []
        tot_status = None
        for (rate, tries) in rate_arr:
            s_delay, s_tries = packet_stats(data, self.packet_num, rate)

            # Correct for the extra packet transmission at the 0 rate
            if s_tries >= 20:
                s_delay = s_delay - self.baseline

            # If it would take more tries than we have
            if s_tries > tries:
                tot_tries.append((rate, tries))
                self.histogram[rate] += tries
                tot_delay += s_delay * (tries / s_tries)
            else: # We successfully transmit the packet
                tot_tries.append((rate, s_tries))
                self.histogram[rate] += s_tries
                tot_delay += s_delay
                tot_status = True # Success
                break
        else:
            tot_status = False # Failure

        if DEBUG:
            print(" => {}: {} ns".format("Good" if tot_status else "Fail",
                                         tot_delay), end=" ")
            for (rate, tries) in tot_tries:
                print("Rate {}/{}".format(rate, tries), end=" ")
            print()

        self.push_statistics(tot_status, self.clock, tot_delay, tot_tries)

        self.packet_num += 1
        self.clock += tot_delay
        return tot_status

    def run(self, n):
        self.clock = 0
        self.packet_num = 0

        i = 0
        while i < n:
            status = self.send_packet()
            if status:
                i += 1

        return (self.clock, self.packet_num - n)

if __name__ == "__main__":
    if len(sys.argv) > 2:
        alg = sys.argv[1]
        data_file = sys.argv[2]
    else:
        print("USAGE: harness.py <algorithm> <data-file> [seed]")
        sys.exit()

    if len(sys.argv) >= 4:
        seed = int(sys.argv[3])
    else:
        seed = random.randint(0, sys.maxsize)

    random.seed(seed)
    print("Running with random seed {}".format(seed))

    data = load_data(data_file)
    module = __import__(alg)
    harness = Harness(data, module.apply_rate, module.process_feedback)
    time, fail = harness.run(len(data))
    if DEBUG: print()
    print("[summary] {:.2f} s to send {} packets ({} failures)".format(time / 1e9, len(data), fail))
    throughput = 1500 * 8 * len(data) / (time / 1e9) / 1e6
    print("Average packet took {:.3f} ms / achieved {:.3f} Mbps".format(time / len(data) / 1e6, throughput))

    for rate_idx, tries in enumerate(harness.histogram):
        if not tries: continue
        mbps = common.RATES[rate_idx][-1] / 2
        print("{} Mbps : {} tries".format(str(mbps).rjust(5),
                                          str(int(tries)).rjust(4)))
