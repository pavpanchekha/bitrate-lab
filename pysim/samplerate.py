# This module implements the SampleRate bit rate selection algorithm
# as outlined in John Bicket's MIT Master's Thesis.

# The algorithm still has the same structure as the original, but is
# wrapped in a class to allow overloading various components.

from __future__ import division

import random
import rates
from collections import namedtuple

class SampleRate(object):
    # Constants: send 1500 bytes at a time, with 1 try each in the MRR
    NBYTES = 1500
    NTRIES = 1

    #"To calculate the transmission time of a n-byte unicast packet given
    # the bit-rate b and number of retries r, SampleRate uses the
    # following equation based on the 802.11 unicast retransmission
    # mechanism detailed in Section 2.2"

    Packet = namedtuple("Packet", ["time_sent", "success", "txTime", "rate"])

    class Rate:
        """ A class to store per-rate information for SampleRate """

        # The average back-off period, in microseconds, for up to 8 attempts
        # of a 802.11b unicast packet.
        # TODO: find g data
        backoff = [0, 155, 315, 635, 1275, 2555, 5115]

        def __init__(self, rix):
            self.info = rates.RATES[rix]
            self.idx = rix
            self.rate = self.info.mbps

            self.success = 0
            self.tries = 0
            self.window = [] # Packets received in the last 10s

            self.successive_failures = 0
            self.total_tx = 0
            self.avg_tx = float("inf")

            self.lossless_tx = self.tx_time(0, 1500) # microseconds

        def tx_time(self, retries, nbytes):
            """
            Time to transmit nbytes bytes at this rate with retries failures
            """

            # tx_time(b, r, n) = difs + backoff[r] + \
            #                  + (r + 1)*(sifs + ack + header + (n * 8/b)

            #"where difs is 50 microseconds in 802.11b and 28 microseconds in
            # 802.11a/g, sifs is 10 microseconds for 802.11b and 9 for
            # 802.11a/g, and ack is 304 microseconds using 1 megabit
            # acknowledgments for 802.11b and 200 microseconds for 6 megabit
            # acknowledgments.  header is 192 microseconds for 1 megabit
            # 802.11b packets, 96 for other 802.11b bit-rates, and 20 for
            # 802.11a/g bit-rates. backoff(r) is calculated using the table"

            rate = rates.RATES[self.idx]
            version = "g" if rate.phy == "ofdm" else "b"

            difs = 50 if version == "b" else 28
            sifs = 10 if version == "b" else 9
            ack = 304 # Somehow 6mb acks aren't used
            header = 192 if rate.code == 0 else 96 if version == "b" else 20

            backoff_r = self.backoff[retries] if retries < len(self.backoff) \
                        else self.backoff[-1]

            return difs + backoff_r + \
                (retries + 1) * (sifs + ack + header + (nbytes * 8 / rate.mbps))



    # The modulation scheme used in 802.11g is orthogonal
    # frequency-division multiplexing (OFDM) copied from 802.11a with data
    # rates of 6, 9, 12, 18, 24, 36, 48, and 54 Mbit/s, and reverts to CCK
    # (like the 802.11b standard) for 5.5 and 11 Mbit/s and
    # DBPSK/DQPSK+DSSS for 1 and 2 Mbit/s.  Even though 802.11g operates
    # in the same frequency band as 802.11b, it can achieve higher data
    # rates because of its heritage to 802.11a.
    RATES = [Rate(i) for i in range(len(rates.RATES))]

    def __init__(self):
        self.npkts = 0
        self.nsuccess = 0
        self.currRate = self.RATES[-1] #current best bitRate

    def apply_rate(self, cur_time):
        self.remove_stale_results(cur_time)

        #"Increment the number of packets sent over the link"
        self.npkts += 1

        #"If no packets have been successfully acknowledged, return the
        # highest bit-rate that has not had 4 successive failures."
        if self.nsuccess == 0:
            for rate in sorted(self.RATES, key=lambda rate: rate.rate, reverse=True):
                if rate.successive_failures < 4:
                    self.currRate = rate
                    return [(rate.idx, self.NTRIES)]

        # Every 10 packets, select a random non-failing bit rate w/ better avg tx
        #"If the number of packets sent over the link is a multiple of ten,"
        if (self.nsuccess != 0) and (self.npkts%10 == 0):
            #"select a random bit-rate from the bit-rates"
            cavg_tx = self.RATES[self.currRate.idx].avg_tx

            #"that have not failed four successive times and that have a
            # minimum packet transmission time lower than the current
            # bit-rate's average transmission time."
            eligible = [r for r in self.RATES
                        if r.lossless_tx < cavg_tx and r.successive_failures < 4]

            if len(eligible) > 0:
                sampleRate = random.choice(eligible)
                return [(sampleRate.idx, self.NTRIES)]

        #"Otherwise, send packet at the bit-rate that has the lowest avg
        # transmission time"
        # Trusts that currRate is properly maintained to be lowest avg_tx
        return [(self.currRate.idx, self.NTRIES)]


    #"When process_feedback() runs, it updates information that tracks
    # the number of samples and recalculates the average transmission time
    # for the bit-rate and destination. process_feedback() performs the
    # following operations:"
    def process_feedback(self, status, timestamp, delay, tries):
        rix, nretries = tries[0]

        if status:
            nretries -= 1 # the last send was successful

        #"Calculate the transmission time for the packet based on the
        # bit-rate and number of retries using Equation 5.1 below."

        tx = self.RATES[rix].tx_time(nretries, self.NBYTES)

        #"Look up the destination and add the transmission time to the
        # total transmission times for the bit-rate."

        br = self.RATES[rix]

        if not status:
            br.successive_failures += 1
            #"If the packet failed, increment the number of successive
            # failures for the bit-rate.
        else:
            #"Otherwise reset it."
            br.successive_failures = 0

            #"If the packet succeeded, increment the number of successful
            # packets sent at that bit-rate.
            br.success += 1
            self.nsuccess += 1

        #"Re-calculate the average transmission time for the bit-rate
        # based on the sum of trans- mission times and the number of
        # successful packets sent at that bit-rate."

        br.total_tx += tx

        if br.success == 0:
            br.avg_tx = float("inf")
        else:
            br.avg_tx = br.total_tx/br.success

        #"Set the current-bit rate for the destination to the one with the
        # minimum average transmission time."
        self.calculateMin()

        #"Append the current time, packet status, transmission time, and
        # bit-rate to the list of transmission results."
        p = self.Packet(timestamp, status, tx, rates.RATES[rix].mbps)
        br.window.append(p)

    #"SampleRate's remove_stale_results() function removes results from
    # the transmission results queue that were obtained longer than ten
    # seconds ago."
    def remove_stale_results(self, cur_time):
        window_cutoff = cur_time - 1e10 #window size of 10s


        for r in self.RATES:
            for p in r.window:
                #"For each stale transmission result, it does the following"
                if p.time_sent < window_cutoff:
                    #"Remove the transmission time from the total
                    # transmission times at that bit-rate to that
                    # destination."
                    r.window.remove(p)
                    r.total_tx -= p.txTime

                    #"If the packet succeeded, decrement the number of
                    # successful packets at that bit-rate to that
                    # destination."
                    if p.success:
                        r.success -= 1
            #"After remove stale results() performs these operations for
            #each stale sample, it recalculates the minimum average
            #transmission times for each bit-rate and destination.
            if r.success == 0:
                r.avg_tx = float("inf")
            else:
                r.avg_tx = r.total_tx/r.success

        for r in self.RATES:
            successive_failures = 0
            maxSuccFails = 0

            for p in r.window:
                if p.success:
                    if successive_failures > maxSuccFails:
                        maxSuccFails = successive_failures
                    successive_failures = 0
                else:
                    successive_failures += 1
            if successive_failures > maxSuccFails:
                maxSuccFails = successive_failures

            r.successive_failures = maxSuccFails


        #"remove_stale_results() then sets the current bit-rate for each
        # destination to the one with the smallest average trans- mission
        # time."
        self.calculateMin()


    def calculateMin(self):
        c = self.RATES[self.currRate.idx]
        if c.successive_failures > 4:
            c.avg_tx = float("inf")

        for r in sorted(self.RATES, key=lambda rate: rate.rate, reverse=True):
            if r.rate < c.rate and r.avg_tx == float("inf") \
               and r.successive_failures == 0 and r.lossless_tx < c.avg_tx:
                c = r
                break
            if c.avg_tx > r.avg_tx and r.successive_failures < 4:
                c = r

        self.currRate = c

algorithm = SampleRate()
apply_rate = algorithm.apply_rate
process_feedback = algorithm.process_feedback

def initialize(time):
    pass
