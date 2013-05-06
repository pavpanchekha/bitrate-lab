# Colleen Josephson, 2013
# This file implements a slightly modified version (I think) of the JBicket MS thesis
# It uses retry chain for the initial send, and seems to get a slightly higher throughput
# interestingly, adding retry chains for normal sends seems to decrease throughput

from random import choice 
from common import ieee80211_to_idx
import common

npkts = 0 #number of packets sent over link
nsuccess = 0 #number of packets sent successfully 
NBYTES = 1500 #constant
currRate = 54 #current best bitRate
NRETRIES = 20

# The average back-off period, in microseconds, for up to 8 attempts of a 802.11b unicast packet. 
# TODO: find g data
backoff = {0:0, 1:155, 2:315, 3:635, 4:1275, 5:2555, 6:5115, 7:5115, 8:5115, 9:5115,
           10:5115, 11:5115, 12:5115, 13:5115, 14:5115, 15:5115, 16:5115, 17:5115,
           18:5115, 19:5115, 20:5115}

#To calculate the transmission time of a n-byte unicast packet given the bit-rate b and
#number of retries r, SampleRate uses the following equation based on the 802.11 unicast
# tx_time(b, r, n) =  difs + backoff[r] + (r + 1)*(sifs + ack + header + (n * 8/b))
def tx_time(bitrate, retries, nbytes):
    global currRate, npkts, nsuccess, NBYTES
    difs = 28 #DCF Interframe Space (DIFS), 28 microseconds in 802.11g
    sifs = 9 #Short Interframe Space (SIFS), 9 microseconds for 802.11g
    ack = 200 #in microseconds, for 6 megabit acknowledgements
    header = 20 #in microseconds, for 802.11 a/g bitrates
    return difs + backoff[retries] + (retries+1)*(sifs + ack + header + (nbytes * 8/bitrate))

class Packet:
    def __init__(self, time_sent, success, txTime, rate):
        self.time_sent = time_sent
        self.success = success
        self.txTime = txTime
        self.rate = rate

    def __repr__(self):
        return ("Pkt sent at time %r, rate %r was successful: %r\n" 
                % (self.time_sent, self.rate, self.success))


class Rate:
    def __init__(self, rate):
        self.rate = rate #in mbps
        self.success = 0
        self.tries = 0
        self.pktAcked = 0
        self.succFails = 0
        self.totalTX = 0
        self.avgTX = float("inf")
        #pktsize/channelrate. pktsize = 1500 bytes
        self.losslessTX = tx_time(rate, 0, 1500)
        self.window = [] #packets rcvd in last 10s

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
rates = dict((r, Rate(r)) for r in [1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])

#multi-rate retry returns an array of (rate, ntries) for the next n packets
#cur_time is in nanoseconds
def apply_rate(cur_time):
    global currRate, npkts, nsuccess, NBYTES, NRETRIES
    remove_stale_results(cur_time)
    
    npkts += 1
    
    #If no packets have been successfully acknowledged, 
    #return the highest bit-rate that has not had 4 successive failures.
    if nsuccess == 0:
        #print("------------------------------------------------")
        #print("NSUCCESS == 0")
        #print("------------------------------------------------")
        rrates = [r[1] for r in sorted(rates.items())]
        rrates.reverse()
        retry = []
        for r in rrates:
            if r.succFails < 4:
                currRate = r.rate
                retry.append((ieee80211_to_idx(currRate)[0], NRETRIES))
    

    #every 10 packets, select a random non-failing bit rate w/ better avg tx
    if (npkts != 0) and (npkts%10 == 0):
        #print("------------------------------------------------")
        #print("TRYING RANDOM RATE")
        #print("------------------------------------------------")
        cavgTX = rates[currRate].avgTX
        eligible = []
        for r in rates.values():
            if r.losslessTX < cavgTX and r.succFails < 4:
                eligible.append(r)
        if len(eligible) > 0:
            currRate = choice(eligible).rate #select random rate from eligible
    #else:        
    #    print("------------------------------------------------")
    #    print("bizniz as usual")
    #    print("------------------------------------------------")
    #Otherwise, send packet at the bit-rate that has the lowest avg xmisscurion time
    #print("cur rate is %r\n" % currRate)
    #print(ieee80211_to_idx(currRate))
    
    #rrates = [r[1] for r in sorted(rates.items())]
    #rrates.reverse()
    #retry = []
    #for r in rrates:
    #    if r.succFails < 4 and r.rate <= currRate: 
    #        retry.append((ieee80211_to_idx(r.rate)[0], NRETRIES))
    #return retry
    return [(ieee80211_to_idx(currRate)[0], NRETRIES)]



#status: true if packet was rcvd successfully
#timestamp: time pkt was sent
#delay: rtt for entire process (inluding multiple tries) in nanoseconds
#tries: an array of (bitrate, nretries) 
def process_feedback(status, timestamp, delay, tries):
    global currRate, npkts, nsuccess, NBYTES
    for t in tries:
        (bitrate, nretries) = t
    
        nretries -= 1
        bitrate = common.RATES[bitrate][-1]/2.0

        tx = tx_time(bitrate, nretries, NBYTES)
        
        br = rates[bitrate]
        br.totalTX += tx

        #we know a packet failed if it it 20 retries
        if not status:
            br.succFails += 1
        else:
            br.success += 1
            br.succFails = 0
            nsuccess += 1

        #caclulate average TX time
        if br.success == 0:
            br.avgTX = float("inf")
        else: br.avgTX = br.totalTX/br.success
    
        #instantiate pkt object
        p = Packet(timestamp, status, tx, bitrate)

        #add packet to window
        br.window.append(p)

        #set current rate to the one w/ min avg tx time
    calculateMin()
    

def remove_stale_results(cur_time):
    window_cutoff = cur_time - 1e10 #window size of 10s

    for r in rates.values():
        #print(r)
        for p in r.window:
            if p.time_sent < window_cutoff:
                r.window.remove(p)
                #remove this pkts contrib. to total TX
                r.totalTX -= p.txTime
                #decrement total number of successes for br
                if p.success:
                    r.success -= 1
        #recalculate avgTX
        if r.success == 0:
            r.avgTX = float("inf")
        else: r.avgTX = r.totalTX/r.success
    
    calculateMin()
        

def calculateMin():
    global currRate, npkts, nsuccess, NBYTES
    #set current rate to the one w/ min avg tx time
    c = rates[currRate]
    if c.succFails > 4:
        c.avgTX = float("inf")
        #c = rates[1]

    rrates = [r[1] for r in sorted(rates.items())]
    rrates.reverse()
    for r in rrates:
        #we've never tried this rate thoroughly before
        if r.rate < c.rate and r.avgTX == float("inf") and r.succFails == 0 and r.losslessTX < c.avgTX:
            c = r
            break
        
        if c.avgTX > r.avgTX and r.succFails < 4:
            c = r
            
    currRate = c.rate
    
