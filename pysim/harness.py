from __future__ import print_function
from __future__ import division
import time
import common
import os, sys
import random

DEBUG = "DEBUG" in os.environ

WINDOW = 1e7 # 10ms

def load_data(source):
    return eval(open(source, "rt").read())

LUOPS = 0
def packet_stats(data, cache, time, rate):
    global LUOPS
    
    txs = []

    while not txs:
        idx, w = cache[rate]
        cache[rate][0] = 0
        
        for i in range(idx, len(data[rate])):
            t, success, delay = data[rate][i]
            LUOPS += 1
            
            if abs(t - time) < w:
                txs.append((success, delay))
                if not cache[rate][0]:
                    cache[rate][0] = i
                    cache[rate][1] = min(w / 1.5, WINDOW)

            if t > w + time:
                break

        cache[rate][1] *= 2

    successful = [tx[1] for tx in txs if tx[0]]

    return (len(successful) / len(txs), 
            sum(successful) / sum([tx[1] for tx in txs]))

class Harness:
    def __init__(self, data, choose_rate, push_statistics):
        self.start = data[0]
        self.data = data[1]
        self.cache = [[0, WINDOW] for i in self.data]
        self.end = data[2]

        self.clock = data[0]
        self.choose_rate = choose_rate
        self.push_statistics = push_statistics

        self.histogram = [[0, 0] for i in common.RATES]

        self.attempts = 0

    def send_one(self, rate, is_success):
        delay = common.tx_time(rate, 1, 1500)

        if is_success:
            delay += common.difs(rate)
            self.attempts = 0
        else:
            self.attempts += 1
            delay += common.backoff(rate, self.attempts)

        self.histogram[rate][0] += 1
        self.histogram[rate][1] += 1 if is_success else 0

        return delay

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
            p_success, a_delay = packet_stats(self.data, self.cache, self.clock, rate)

            s_tries = 0
            succeeded = False
            for i in range(tries):
                success = random.random() < p_success
                s_tries += 1
                tot_delay += self.send_one(rate, success)

                if success:
                    succeeded = True
                    break

            tot_tries.append((rate, s_tries))

            if succeeded:
                tot_status = True
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

        self.clock += tot_delay
        return tot_status

    def run(self):
        self.clock = self.start

        good = 0
        bad = 0
        print("Please wait, running simulation:     ", end="")
        lenlast = 0
        try:
            while self.clock < self.end:
                pct = int(100 * (self.clock-self.start) / (self.end-self.start))

                print("\b" * lenlast, end="")
                msg = "{: 3d}%, {}".format(pct, LUOPS)
                lenlast = len(msg)
                print(msg, end="")
                sys.stdout.flush()

                status = self.send_packet()
                if status:
                    good += 1
                else:
                    bad += 1
        except KeyboardInterrupt as e:
            pass
        print()

        time = self.clock - self.start

        return time, good, bad

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
    time, good, bad = harness.run()
    
    if DEBUG: print()

    print("Simulation ran with {} LUOPS".format(LUOPS))
    print("[summary] {:.2f} s to send {} packets (and {} failures)".format(time / 1e9, good, bad))
    throughput = 1500 * 8 * good / (time / 1e9) / 1e6
    print("Average packet took {:.3f} ms / achieved {:.3f} Mbps".format(time / good / 1e6, throughput))

    for rate_idx, info in enumerate(harness.histogram):
        tries, successes = info
        if not tries: continue

        mbps = common.RATES[rate_idx][-1] / 2
        print("{:>5} Mbps : {:>4} tries ({:.0%} success rate)".format(
            mbps, tries, successes/tries))
