# Colleen Josephson, 2013
# This file attempts to implement the minstrel rate control algorithm from the
# 3.3.8 linux kernel. We assume multi-rate retry capabilities, so we omit 
# the code for the non-mrr case. 

from __future__ import division

import random
import common
import math
from common import ieee80211_to_idx

packet_count = 0 #number of packets sent over link
nsuccess = 0 #number of packets sent successfully 
nlookaround = 0
currRate = 54  #current best bitRate
bestThruput = 12
nextThruput = 11
bestProb = 2
lowestRate = 1
time_last_called = 0
cw_min = 15
cw_max = 1023
segment_size = 6000
max_retry = 7 #safe default specified in kernel code
probeFlag = False

sample_count = 0
sample_deferred = 0

SAMPLING_RATIO = 10

def tx_time(mbps, length=1200): #rix is index to RATES, length in bytes
    '''
    Adapted from 802.11 util.c ieee80211_frame_duration()

    calculate duration (in microseconds, rounded up to next higher
    integer if it includes a fractional microsecond) to send frame of
    len bytes (does not include FCS) at the given rate. Duration will
    also include SIFS.
    '''

    rateinfo = common.RATES[common.ieee80211_to_idx(mbps)]

    if rateinfo.phy == "ofdm":
        '''
        OFDM:
        N_DBPS = DATARATE x 4
        N_SYM = Ceiling((16+8xLENGTH+6) / N_DBPS)
        (16 = SIGNAL time, 6 = tail bits)
        TXTIME = T_PREAMBLE + T_SIGNAL + T_SYM x N_SYM + Signal Ext

        T_SYM = 4 usec
        802.11a - 17.5.2: aSIFSTime = 16 usec
        802.11g - 19.8.4: aSIFSTime = 10 usec + signal ext = 6 usec
        '''
        dur = 16 # SIFS + signal ext */
        dur += 16 # 17.3.2.3: T_PREAMBLE = 16 usec */
        dur += 4 # 17.3.2.3: T_SIGNAL = 4 usec */
        dur += 4 * (math.ceil((16+8*(length+4)+6)/(4*mbps))+1) # T_SYM x N_SYM

    else:
        '''
        802.11b or 802.11g with 802.11b compatibility:
        18.3.4: TXTIME = PreambleLength + PLCPHeaderTime +
        Ceiling(((LENGTH+PBCC)x8)/DATARATE). PBCC=0.

        802.11 (DS): 15.3.3, 802.11b: 18.3.4
        aSIFSTime = 10 usec
        aPreambleLength = 144 usec or 72 usec with short preamble
        aPLCPHeaderLength = 48 usec or 24 usec with short preamble
        '''
        dur = 10 # aSIFSTime = 10 usec
        dur += (72 + 24) #using short preamble, otw we'd use (144 + 48)
        dur += math.ceil((8*(length + 4))/mbps)+1

    return dur

class Rate:
    #OFDM = g
    def __init__(self, rate):
        self.rate = rate #in mbps
        self.throughput = 0 #in bits per second
        self.last_update = 0.0 #timestamp of last update, ns(?)
        #ewma obj. can return probability of success. if you ask nicely.
        self.ewma = common.EWMA(0.0, 100e6, 0.75) #100e6 = 100 ms,
        self.succ_hist = 0 #total successes ever
        self.att_hist = 0 #total xmission attempts ever
        self.success = 0  #number of successful xmissions in cur time interval
        self.attempts = 0 #number of attempted transmissions in cur time interval
        self.losslessTX = tx_time(rate, 1200) #microseconds, pktsize 1200 in kernel,
        self.ack = tx_time(rate, 10) #microseconds, assumes 1mbps ack rate

        #what is the difference between these?
        self.sample_limit = -1
        self.retry_count = 1

        #a complicated loop to calculate the initial adjusted retry count
        tx_time_ = self.losslessTX + self.ack#includes ack
        condition = True
        while condition:
            #add one retransmission
            tx_time_single = self.ack + self.losslessTX

            #contention window
            cw = cw_min
            tx_time_single += (9* cw) >> 1;
            cw = min((cw << 1) | 1, cw_max)
            
            tx_time_ += tx_time_single

            self.retry_count += 1
            condition = (tx_time_ < segment_size) and (self.retry_count  < 
                                                      max_retry)
        self.adjusted_retry_count = self.retry_count #Max retrans. used for probing

    def __repr__(self):
        return ("Bitrate %r mbps: \n"
                "  attempts: %r \n"
                "  pktsAcked: %r \n"
                "  thruput: %r microseconds \n"
                "  probSuccess: %r \n"
                "  losslessTX: %r microseconds"
                % (self.rate, self.attempts, self.success, 
                   self.throughput, self.ewma.read(), self.losslessTX))

# The modulation scheme used in 802.11g is orthogonal frequency-division multiplexing 
# (OFDM)copied from 802.11a with data rates of 6, 9, 12, 18, 24, 36, 48, and 54 Mbit/s,
# and reverts to CCK (like the 802.11b standard) for 5.5 and 11 Mbit/s and DBPSK/DQPSK+# DSSS for 1 and 2 Mbit/s. Even though 802.11g operates in the same frequency band as 8# 02.11b, it can achieve higher data rates because of its heritage to 802.11a.
rates = dict((r, Rate(r)) for r in [1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])


# 10 times a second (this frequency is alterable by changing the driver code) a timer
# fires, which evaluates the statistics table. EWMA calculations (described below) 
# are used to process the success history of each rate. On completion of the 
# calculation, a decision is made as to the rate which has the best throughput, 
# second best throughput, and highest probability of success. This data is used for 
# populating the retry chain during the next 100 ms. Note that the retry chain is 
# described below.
def apply_rate(cur_time): #cur_time is in nanoseconds
    global packet_count, nsuccess, nlookaround, currRate, sample_count, sample_deferred
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called

    if cur_time - time_last_called >= 1e8:
        update_stats(cur_time)
        time_last_called = cur_time

    #Minstrel spends a particular percentage of frames, doing "look around" i.e. 
    #randomly trying other rates, to gather statistics. The percentage of 
    #"look around" frames defaults to 10%. The distribution of lookaround frames is
    #also randomized somewhat to avoid any potential "strobing" of lookaround 
    #between similar nodes.
    
    #Try |         Lookaround rate              | Normal rate
    #    | random < best    | random > best     |
    #--------------------------------------------------------------
    # 1  | Best throughput  | Random rate       | Best throughput
    # 2  | Random rate      | Best throughput   | Next best throughput
    # 3  | Best probability | Best probability  | Best probability
    # 4  | Lowest Baserate  | Lowest baserate   | Lowest baserate
    delta = (packet_count * SAMPLING_RATIO / 100) - (sample_count + sample_deferred // 2)

    if delta > 0:
        #"Analysis of information showed that the system was sampling
        # too hard at some rates. For those rates that never work
        # (54mb, 500m range) there is no point in sending 10 sample
        # packets (< 6 ms time). Consequently, for the very very low
        # probability rates, we sample at most twice."
        
        if packet_count >= 10000:
            sample_count = 0
            packet_count = 0
            sample_deferred = 0
        elif delta > len(rates) * 2:
            #"With multi-rate retry, not every planned sample          
            # attempt actually gets used, due to the way the retry     
            # chain is set up - [max_tp,sample,prob,lowest] for        
            # sample_rate < max_tp.                                    
            #                                                          
            # If there's too much sampling backlog and the link        
            # starts getting worse, minstrel would start bursting      
            # out lots of sampling frames, which would result          
            # in a large throughput loss."
            sample_count += delta  - (len(rates)*2)
            

        randrate = 1
        while(randrate == 1): #never sample at lowest rate
            randrate = random.choice(rates.keys())

        if randrate < bestThruput:
            chain = [bestThruput, randrate, bestProb, lowestRate]
            ''' FROM KERNEL:
            /* Only use IEEE80211_TX_CTL_RATE_CTRL_PROBE to mark        
            * packets that have the sampling rate deferred to the      
            * second MRR stage. Increase the sample counter only       
            * if the deferred sample rate was actually used.           
            * Use the sample_deferred counter to make sure that        
            * the sampling is not done in large bursts */'''
            probe_flag = True
            sample_deferred += 1

        else:
            #manages probe counting
            if rates[randrate].sample_limit != 0:
                sample_count += 1
                if rates[randrate].sample_limit > 0:
                    rates[randrate].sample_limit -= 1
            
            chain = [randrate, bestThruput, bestProb, lowestRate]
    
    else:     #normal
        chain = [bestThruput, nextThruput, bestProb, lowestRate]

    mrr = [(ieee80211_to_idx(rate), rates[rate].adjusted_retry_count)
           for rate in chain]

    return mrr
        
#status: true if packet was rcvd successfully
#timestamp: time pkt was sent
#delay: rtt for entire process (inluding multiple tries) in nanoseconds
#tries: an array of (bitrate, nretries) 
def process_feedback(status, timestamp, delay, tries):
    global packet_count, nsuccess, nlookaround, currRate, probeFlag
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called, sample_deferred, sample_count
    for t in range(len(tries)):
        (bitrate, br_tries) = tries[t]
        if br_tries > 0:
            bitrate = common.RATES[bitrate].dot11_rate
            #if bitrate == 1:
            
            br = rates[bitrate]
            br.attempts = (br.attempts + br_tries) 
            packet_count += br_tries

            #if the packet was successful...
            if status and t == (len(tries)-1):
                br.success = (br.success + 1) 
                nsuccess = (nsuccess + 1) 

    #if we had the random rate second in the retry chain, and actually ended up
    #using it, increment the count and unset the flag
    if t > 1 and probeFlag:
        sample_count += 1
        probeFlag = False

    if sample_deferred > 0:
        sample_deferred -= 1

    if timestamp - time_last_called >= 1e8:
        self.update_stats(timestamp)


def update_stats(timestamp):
    global bestThruput, nextThruput, bestProb, rates

    for i, br in rates.items():
        if br.attempts: #prevents divide by 0
            p = br.success * 18000 // br.attempts
            br.succ_hist += br.success
            br.att_hist += br.attempts
            br.ewma.feed(timestamp, p)
        p = br.ewma.read()
        

        if p and (p > 17100 or p < 1800):
            br.adjusted_retry_count = br.retry_count >> 1
            if br.adjusted_retry_count > 2:
                br.adjusted_retry_count = 2
            br.sample_limit = 4
        else:
            br.sample_limit = -1
            br.adjusted_retry_count = br.retry_count

        if br.adjusted_retry_count == 0:
            br.adjusted_retry_count = 2
        
        br.success = 0
        br.attempts = 0
        br.throughput = throughput(p, br.losslessTX)

    br.last_update = timestamp #was self.update, changed to br.update -CJ

    #changed rates to rates_, changed rates to rates.values() -CJ
    rates_ = sorted(rates.values(), key=lambda br: br.throughput, reverse=True)
    bestThruput = rates_[0].rate

    nextThruput = rates_[1].rate
    #probably should be best prob that's not 1mbps, since othwerwise it would be
    # redundant to lowest base rate in retry chain
    rates_.remove(rates[1])
    bestProb = max(rates_, key=lambda br: br.ewma.read() if br.ewma.read() else 0).rate#, reverse=True) -CJ

# thru = p_success [0, 18000] / lossless xmit time in ms
def throughput(psuccess, rtt):
    if psuccess:
        return psuccess*(1e6/rtt)
    else: return 0

