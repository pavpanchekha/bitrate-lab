# Colleen Josephson, 2013
# This file attempts to implement the SampleRate bit rate selection algorithm 
# as outlined in the JBicket MS Thesis.

import time

#number of packets sent over link
npkts = 0

# The average back-off period, in microseconds, for up to 8 attempts of a 802.11b unicast packet. 
# TODO: find g data
backoff = {0:0, 1:155, 2:315, 3:635, 4:1275, 5:2555, 6:5115, 7:5115, 8:5115}

#To calculate the transmission time of a n-byte unicast packet given the bit-rate b and
#number of retries r, SampleRate uses the following equation based on the 802.11 unicast
# tx_time(b, r, n) =  difs + backoff[r] + (r + 1)*(sifs + ack + header + (n * 8/b))
def tx_time(bitrate, retries, nbytes):
    difs = 28 #DCF Interframe Space (DIFS), 28 microseconds in 802.11g
    sifs = 9 #Short Interframe Space (SIFS), 9 microseconds for 802.11g
    ack = 200 #in microseconds, for 6 megabit acknowledgements
    header = 20 #in microseconds, for 802.11 a/g bitrates
    return difs + backoff[retries] + (retries+1)*(sifs + ack + header + (nbytes * 8/bitrate))

class Packet:
    def __init__(self, time_sent, success, rate):
        self.time_sent = time_sent
        self.success = success
        self.rate = rate

    def __repr__(self):
        return ("Pkt sent at time %r, rate %r was successful: %r\n" 
                % (self.time_sent, self.rate, self.success))
    

class Rate:
    def __init__(self, rate):
        self.rate = rate #in mbps
        self.tries = 0
        self.pktAcked = 0
        self.succFails = 0
        self.totalTX = 0
        self.avgTX = None
        #pktsize/channelrate. pktsize = 1500 bytes
        self.losslessTX = tx_time(rate, 0, 1500)
        self.window = set([]) #packets rcvd in last 10s

    def avg_tx(self):
        # Only calculates the average transmission time over packets 
        # that were sent within the last averaging window.
        window_cuttoff = time.time() - 10
        
        self.totalTX = 0
        for p in window:
            if p.time_sent < window_cutoff:
                self.remove(p)
            else:
                self.totalTX += #TODO
            
    def __repr__(self):
        return ("Bitrate %r mbps: \n"
                "  tries: %r \n"
                "  pktsAcked: %r \n"
                "  succFails: %r \n"
                "  totalTX: %r microseconds \n"
                "  avgTx: %r microseconds \n"
                "  losslessTX: %r microseconds"
                % (self.rate, self.tries, self.pktAcked, self.succFails, 
                   self.totalTX, self.avgTX, self.losslessTX))


# The modulation scheme used in 802.11g is orthogonal frequency-division multiplexing (OFDM)
# copied from 802.11a with data rates of 6, 9, 12, 18, 24, 36, 48, and 54 Mbit/s, and reverts 
# to CCK (like the 802.11b standard) for 5.5 and 11 Mbit/s and DBPSK/DQPSK+DSSS for 1 and 2 Mbit/s.
# Even though 802.11g operates in the same frequency band as 802.11b, it can achieve higher 
# data rates because of its heritage to 802.11a.
rates = {1:Rate(1), 2:Rate(2), 5.5:Rate(5.5), 6:Rate(6), 9:Rate(9), 11:Rate(11), 12:Rate(12), 18:Rate(18), 24:Rate(24), 36:Rate(36), 48:Rate(48), 54:Rate(54)}

def apply_rate():

    #If no packets have been successfully acknowledged, 
    #return the highest bit-rate that has not had 4 successive failures.
    

    npkts += 1

    #every 10 packets, select a random non-failing bit rate w/ better avg tx
    if (npkts != 0) and (npkts%10 == 0):
        pass

    #Otherwise, send the packet at the bit-rate that has the lowest avg xmission time


def process_feedback(bitrate, nretries, timestamp):
    

def remove_stale_results():
    pass

