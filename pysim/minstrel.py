# Colleen Josephson, 2013
# This file attempts to implement the minstrel rate control algorithm

from random import randint
from random import choice 
import common

npkts = 0 #number of packets sent over link
nsuccess = 0 #number of packets sent successfully 
nlookaround = 0
NBYTES = 1500 #constant
currRate = 54  #current best bitRate
NRETRIES = 20
bestThruput = 54
nextThruput = 48
bestProb = 1
lowestRate = 1
time_last_called = 0
cw_min = 15
cw_max = 1023
segment_size = 6000

# The average back-off period, in milliseconds, for up to 8 attempts of a 802.11b unicast packet. 
# TODO: find g data
backoff = {0:0, 1:.155, 2:.315, 3:.635, 4:1.275, 5:2.555, 6:5.115, 7:5.115, 8:5.115, 9:5.115,
           10:5.115, 11:5.115, 12:5.115, 13:5.115, 14:5.115, 15:5.115, 16:5.115, 17:5.115,
           18:5.115, 19:5.115, 20:5.115}
#1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])
odfm = set([6, 9, 12, 18, 24, 36, 48, 54])

'''
/* calculate duration (in microseconds, rounded up to next higher
* integer if it includes a fractional microsecond) to send frame of
* len bytes (does not include FCS) at the given rate. Duration will
* also include SIFS.
*
* rate is in 1000 kbps (1Mbps)
*/'''
def tx_time(length, rate):
    if rates[rate].odfm:
        '''* OFDM:
        *
        * N_DBPS = DATARATE x 4
        * N_SYM = Ceiling((16+8xLENGTH+6) / N_DBPS)
        *	(16 = SIGNAL time, 6 = tail bits)
        * TXTIME = T_PREAMBLE + T_SIGNAL + T_SYM x N_SYM + Signal Ext
        *
        * T_SYM = 4 usec
        * 802.11a - 17.5.2: aSIFSTime = 16 usec
        * 802.11g - 19.8.4: aSIFSTime = 10 usec +
        *	signal ext = 6 usec
        */'''
        dur = 16 # SIFS + signal ext */
        dur += 16 # 17.3.2.3: T_PREAMBLE = 16 usec */
        dur += 4 # 17.3.2.3: T_SIGNAL = 4 usec */
        dur += 4 * ((16+8*(length+4)+6) + (4*rate-1)/(4*rate)) # T_SYM x N_SYM 

    else:
        '''
        * 802.11b or 802.11g with 802.11b compatibility:
        * 18.3.4: TXTIME = PreambleLength + PLCPHeaderTime +
        * Ceiling(((LENGTH+PBCC)x8)/DATARATE). PBCC=0.
        *
        * 802.11 (DS): 15.3.3, 802.11b: 18.3.4
        * aSIFSTime = 10 usec
        * aPreambleLength = 144 usec or 72 usec with short preamble
        * aPLCPHeaderLength = 48 usec or 24 usec with short preamble
        *'''
        dur = 10 # aSIFSTime = 10 usec 
        dur += (72 + 24) #using short preamble, otw we'd use (144 + 48)
        dur += ((8*(length + 4))+(rate-1))/rate
    
    return dur

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
    #OFDM = g
    def __init__(self, rate):
        self.rate = rate #in mbps

        #if we are an 802.11g rate...
        if rate in odfm:
            self.odfm == True
        else: self.odfm = False

        self.throughput = 0 #in bits per second
        self.last_update = 0.0 
        self.ewma = common.EWMA(0.0, 100e6, 0.75) # 100 ms
        self.succ_hist = 0 #number of successful xmission in previous update interval
        self.att_hist = 0 #number of xmission attempts in previous update interval
        self.success = 0  #number of successful xmissions in cur time interval
        self.attempts = 0 #number of attempted transmissions in cur time interval
        self.losslessTX = tx_time(rate, 1200) #microseconds, pktsize 1200 in kernel,
                self.ack = tx_time(rate, 10) #microseconds, assumes 1mbps ack rate
        self.window = [] #packets rcvd in last 10s

        #what is the difference between these?
        self.sample_limit = -1
        self.retry_count = 1

        #a complicated loop to calculate the initial adjusted retry count
        tx_time_ = self.losslessTX #includes ack
        condition = True
        while condition:
            #add one retransmission
            tx_time_single = self.ack + self.losslessTX

            #contention window
            tx_time_single += (9* cw) >> 1;
            cw = min((cw << 1) | 1, cw_max)
            
            tx_time_ += tx_time_single

            condition = (tx_time_ < segment_size) and (self.retry_count + 1 < 
                                                      max_retry)
        self.adjusted_retry_count = self.retry_count #Max retrans. used for probing

    def __repr__(self):
        return ("Bitrate %r mbps: \n"
                "  attempts: %r \n"
                "  pktsAcked: %r \n"
                "  succFails: %r \n"
                "  totalTX: %r microseconds \n"
                "  avgTx: %r microseconds \n"
                "  losslessTX: %r microseconds"
                % (self.rate, self.attempts, self.success, self.succFails, 
                   self.totalTX, self.avgTX, self.losslessTX))

# The modulation scheme used in 802.11g is orthogonal frequency-division multiplexing (OFDM)
# copied from 802.11a with data rates of 6, 9, 12, 18, 24, 36, 48, and 54 Mbit/s, and reverts 
# to CCK (like the 802.11b standard) for 5.5 and 11 Mbit/s and DBPSK/DQPSK+DSSS for 1 and 2 Mbit/s.
# Even though 802.11g operates in the same frequency band as 802.11b, it can achieve higher 
# data rates because of its heritage to 802.11a.
rates = dict((r, Rate(r)) for r in [1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])


# 10 times a second (this frequency is alterable by changing the driver code) a timer
# fires, which evaluates the statistics table. EWMA calculations (described below) 
# are used to process the success history of each rate. On completion of the 
# calculation, a decision is made as to the rate which has the best throughput, 
# second best throughput, and highest probability of success. This data is used for 
# populating the retry chain during the next 100 ms. Note that the retry chain is 
# described below.
#cur_time is in nanoseconds
def apply_rate(cur_time):
    global npkts, nsuccess, nlookaround, NBYTES, currRate, NRETRIES
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called

    if cur_time - time_last_called >= 1e8:
        update_stats()
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
    if randint(1,100) <= 10:
        #Analysis of information showed that the system was sampling too hard
        #at some rates. For those rates that never work (54mb, 500m range) 
        #there is no point in sending 10 sample packets (< 6 ms time). Consequently, 
        #for the very very low probability rates, we sample at most twice.

        random = choice(rates.values()).rate
        while(random == 1): #never sample at lowest rate
            random = choice(rates.values()).rate

        if random < bestThruput:
            return [(ieee80211_to_idx(bestThruput)[0],
                     rates[bestThruput].adjusted_retry_count),
                    (ieee80211_to_idx(random)[0],
                     rates[random].adjusted_retry_count), 
                    (ieee80211_to_idx(bestProb)[0],
                     rates[bestProb].adjusted_retry_count), 
                    (ieee80211_to_idx(lowestBase)[0],
                     rates[lowestBase].adjusted_retry_count)]
        else:
            
            #TODO: understand the corresponding kernel code more 
            #and implement if (if necessary)
            if rates[random].sample_limit != 0:
                if rates[random].sample_limit > 0:
                    rates[random].sample_limit -= 1
            
            return [(ieee80211_to_idx(random)[0],
                      rates[random].adjusted_retry_count), 
                    (ieee80211_to_idx(bestThruput)[0],
                     rates[bestThruput].adjusted_retry_count),
                    (ieee80211_to_idx(bestProb)[0],
                     rates[bestProb].adjusted_retry_count), 
                    (ieee80211_to_idx(lowestBase)[0],
                     rates[lowestBase].adjusted_retry_count)]
        
    #normal
    return [(ieee80211_to_idx(bestThruput)[0],
             rates(bestThruput).adjusted_retry_count), 
            (ieee80211_to_idx(nextThruput)[0],
             rates(nextThruput).adjusted_retry_count), 
            (ieee80211_to_idx(bestProb)[0],
             rates(bestProb).adjusted_retry_count), 
            (ieee80211_to_idx(lowestRate)[0],
             rates(lowestRate).adjusted_retry_count)]
    
#status: true if packet was rcvd successfully
#timestamp: time pkt was sent
#delay: rtt for entire process (inluding multiple tries) in nanoseconds
#tries: an array of (bitrate, nretries) 
def process_feedback(status, timestamp, delay, tries):
    global npkts, nsuccess, nlookaround, NBYTES, currRate, NRETRIES
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called
    for t in tries:
        (bitrate, nretries) = t
        nretries -= 1
        bitrate = common.RATES[bitrate][-1]/2.0
        
        br = rates[bitrate]
        br.tries = (br.attempts + 1) % 10000
        npkts = (npkts + 1) % 10000

        #if the packet was successful...
        if status:
            br.success = (br.success + 1) % 10000
            nsuccess = (nsuccess + 1) % 10000

        #instantiate pkt object
        p = Packet(timestamp, status, delay, bitrate)

        #add packet to window
        br.window.append(p)

        #throughput, ewma_prob, this_prob, this_succ, this_attempt 
        #all filled out during EWMA firing every 100ms?
        #what do to about initial conditions (the first 100ms)?

        if timestamp - time_last_called >= 1e8:
            self.update_stats()

def update_stats(timestamp):
    global bestThruput, nextThruput, bestProb

    for i, br in rates.items():
        p = br.success * 18000 // br.attempts
        br.succ_hist += br.success
        br.att_hist += br.attempts
        br.ewma.feed(timestamp, p)
        p = br.ewma.read()

        if p > 17100 or p < 1800:
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
        br.throughput = throughput(p / 18000, br.losslessTX)

    self.last_update = timestamp

    rates = sorted(rates, key=lambda br: br.throughput, reverse=True)
    bestThruput = rates[0]
    nextThruput = rates[0]
    bestProb = max(rates, key=lambda br: br.ewma.read(), reverse=True)

# thru = p_success [0, 18000] / lossless xmit time in ms
def throughput(psuccess, rtt, pktsize = NBYTES*8/1000000):
    return psuccess/(1e6/rtt)
