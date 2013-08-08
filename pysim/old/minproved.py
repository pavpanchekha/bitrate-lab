# Colleen Josephson, 2013
# This file attempts to implement the minstrel rate control algorithm

from random import randint
from random import choice 
import rates
from rates import ieee80211_to_idx

class BalancedEWMA:
    def __init__(self, time, time_step, pval):
        self.p = pval
        self.time = time
        self.step = time_step

        self.blocks = 0
        self.denom = 0
        self.val = None

    def feed(self, time, num, denom):
        if self.blocks == 0:
            self.denom = denom
            newval = num / denom
        else:
            avg_block = self.denom / self.blocks
            block_weight = denom / avg_block if avg_block else 1
            relweight = self.p / (1 - self.p)

            prob = num / denom

            newval = (self.val * relweight + prob * block_weight) / \
                     (relweight + block_weight)

        self.blocks += 1
        self.val = newval
        self.time = time

    def read(self):
        if self.val is not None:
            return int(self.val * 18000)
        else:
            return None

npkts = 0 #number of packets sent over link
nsuccess = 0 #number of packets sent successfully 
nlookaround = 0
NBYTES = 1500 #constant
currRate = 54  #current best bitRate
NRETRIES = 20
bestThruput = 12
nextThruput = 11
bestProb = 2
lowestRate = 1
time_last_called = 0
cw_min = 15
cw_max = 1023
segment_size = 6000
max_retry = 7 #safe default specified in kernel code

# The average back-off period, in milliseconds, for up to 8 attempts of a 802.11b unicast packet. 
# TODO: find g data
backoff = {0:0, 1:.155, 2:.315, 3:.635, 4:1.275, 5:2.555, 6:5.115, 7:5.115, 8:5.115, 
9:5.115, 10:5.115, 11:5.115, 12:5.115, 13:5.115, 14:5.115, 15:5.115, 16:5.115, 
17:5.115, 18:5.115, 19:5.115, 20:5.115}
#802.11g rates
odfm = set([6, 9, 12, 18, 24, 36, 48, 54])

'''
/* Adapted from 802.11 util.c ieee80211_frame_duration()
*
* calculate duration (in microseconds, rounded up to next higher
* integer if it includes a fractional microsecond) to send frame of
* len bytes (does not include FCS) at the given rate. Duration will
* also include SIFS.
*/'''
def tx_time(rate, length): #rate is Mbps, length in bytes
    if rate in odfm:
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
        dur += 4* (round((16+8*(length+4)+6)/(4*rate))+1) # T_SYM x N_SYM 

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
        dur += round((8*(length + 4))/rate)+1
    
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
        self.throughput = 0 #in bits per second
        self.last_update = 0.0 #timestamp of last update, ns(?)
        #ewma obj. can return probability of success. if you ask nicely.
        self.ewma = BalancedEWMA(0.0, 100e6, 0.75) #100e6 = 100 ms
        self.succ_hist = 0 #total successes ever
        self.att_hist = 0 #total xmission attempts ever
        self.success = 0  #number of successful xmissions in cur time interval
        self.attempts = 0 #number of attempted transmissions in cur time interval
        self.losslessTX = tx_time(rate, 1200) #microseconds, pktsize 1200 in kernel,
        self.ack = tx_time(rate, 10) #microseconds, assumes 1mbps ack rate
        self.window = [] #packets rcvd in last 10s
        self.tban = 0

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
RATES = dict((r, Rate(r)) for r in [1, 2, 5.5, 6, 9, 11, 12, 18, 24, 36, 48, 54])


# 10 times a second (this frequency is alterable by changing the driver code) a timer
# fires, which evaluates the statistics table. EWMA calculations (described below) 
# are used to process the success history of each rate. On completion of the 
# calculation, a decision is made as to the rate which has the best throughput, 
# second best throughput, and highest probability of success. This data is used for 
# populating the retry chain during the next 100 ms. Note that the retry chain is 
# described below.
def apply_rate(cur_time): #cur_time is in nanoseconds
    global npkts, nsuccess, nlookaround, NBYTES, currRate, NRETRIES
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

    if RATES[bestThruput].tban > 4:
        #print("Temp ban on {}, switching to {}!".format(bestThruput, nextThruput))
        RATES[bestThruput].tban = 0
        bestThruput = nextThruput
        nextThruput = bestProb
    
    if randint(1,100) <= 10 or RATES[bestThruput].tban > 4:
        #Analysis of information showed that the system was sampling too hard
        #at some rates. For those rates that never work (54mb, 500m range) 
        #there is no point in sending 10 sample packets (< 6 ms time). Consequently, 
        #for the very very low probability rates, we sample at most twice.

        random = choice(list(RATES))
        while(random == 1): #never sample at lowest rate
            random = choice(list(RATES))

        if random < bestThruput:
            r = [(ieee80211_to_idx(bestThruput),
                     RATES[bestThruput].adjusted_retry_count),
                    (ieee80211_to_idx(random),
                     RATES[random].adjusted_retry_count), 
                    (ieee80211_to_idx(bestProb),
                     RATES[bestProb].adjusted_retry_count), 
                    (ieee80211_to_idx(lowestRate),
                     RATES[lowestRate].adjusted_retry_count)]
        else:
            #TODO: understand the corresponding kernel code more 
            #and implement if (if necessary)
            if RATES[random].sample_limit != 0:
                if RATES[random].sample_limit > 0:
                    RATES[random].sample_limit -= 1
            
            r = [(ieee80211_to_idx(random),
                      RATES[random].adjusted_retry_count), 
                    (ieee80211_to_idx(bestThruput),
                     RATES[bestThruput].adjusted_retry_count),
                    (ieee80211_to_idx(bestProb),
                     RATES[bestProb].adjusted_retry_count), 
                    (ieee80211_to_idx(lowestRate),
                     RATES[lowestRate].adjusted_retry_count)]
    
    else:     #normal
        r = [(ieee80211_to_idx(bestThruput),
              RATES[bestThruput].adjusted_retry_count), 
             (ieee80211_to_idx(nextThruput),
              RATES[nextThruput].adjusted_retry_count), 
             (ieee80211_to_idx(bestProb),
              RATES[bestProb].adjusted_retry_count), 
             (ieee80211_to_idx(lowestRate),
              RATES[lowestRate].adjusted_retry_count)]
    return r
        
#status: true if packet was rcvd successfully
#timestamp: time pkt was sent
#delay: rtt for entire process (inluding multiple tries) in nanoseconds
#tries: an array of (bitrate, nretries) 
def process_feedback(status, timestamp, delay, tries):
    global npkts, nsuccess, nlookaround, NBYTES, currRate, NRETRIES
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called
    for t in range(len(tries)):
        (bitrate, br_tries) = tries[t]
        if br_tries > 0:
            bitrate = rates.RATES[bitrate].mbps
            #if bitrate == 1:
            
            br = RATES[bitrate]
            br.attempts = (br.attempts + br_tries) 
            npkts = (npkts + 1) 

            #if the packet was successful...
            if status and t == (len(tries)-1):
                br.success = (br.success + 1) 
                nsuccess = (nsuccess + 1) 

                br.tban = 0
            else:
                br.tban += 1

            #instantiate pkt object
            p = Packet(timestamp, status, delay, bitrate)
            
            #add packet to window
            br.window.append(p)
        
    if timestamp - time_last_called >= 1e8:
        self.update_stats(timestamp)

USCNT = 0
def update_stats(timestamp):
    global bestThruput, nextThruput, bestProb, RATES, USCNT

    USCNT += 1

    if USCNT % 100 == 0:
        for br in RATES.values():
            br.tban = 0

    for i, br in RATES.items():
        if br.attempts: #prevents divide by 0
            br.succ_hist += br.success
            br.att_hist += br.attempts
            br.ewma.feed(timestamp, br.success, br.attempts)
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
    rates_ = sorted(RATES.values(), key=lambda br: br.throughput, reverse=True)
    bestThruput = rates_[0].rate

    nextThruput = rates_[1].rate
    #probably should be best prob that's not 1mbps, since othwerwise it would be
    # redundant to lowest base rate in retry chain
    rates_.remove(RATES[1])
    bestProb = max(rates_, key=lambda br: br.ewma.read() if br.ewma.read() else 0).rate#, reverse=True) -CJ

# thru = p_success [0, 18000] / lossless xmit time in ms
def throughput(psuccess, rtt):
    if psuccess:
        return psuccess*(1e6/rtt)
    else: return 0

