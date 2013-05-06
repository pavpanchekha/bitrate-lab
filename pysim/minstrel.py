# Colleen Josephson, 2013
# This file attempts to implement the minstrel rate control algorithm

from random import randint
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

# The average back-off period, in milliseconds, for up to 8 attempts of a 802.11b unicast packet. 
# TODO: find g data
backoff = {0:0, 1:.155, 2:.315, 3:.635, 4:1.275, 5:2.555, 6:5.115, 7:5.115, 8:5.115, 9:5.115,
           10:5.115, 11:5.115, 12:5.115, 13:5.115, 14:5.115, 15:5.115, 16:5.115, 17:5.115,
           18:5.115, 19:5.115, 20:5.115}


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
        self.throughput = 0

        self.last_update = 0.0
        self.ewma = common.EWMA(0.0, 100e6, 0.75) # 100 ms
        self.success = 0
        self.tries = 0
        self.succ_hist = 0
        self.att_hist = 0

        #This succ/attempt reports how many packets were sent 
        #(and number of successes) in the last time interval.
        self.this_succ = 0
        self.this_attempt = 0
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
                % (self.rate, self.tries, self.success, self.succFails, 
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
        #Analysis of information showed that the system was sampling too hard at some rates. 
        #For those rates that never work (54mb, 500m range) there is no point in sending 
        #10 sample packets (< 6 ms time). Consequently, for the very very low probability rates, 
        #we sample at most twice.
        pass
    
    #normal
    
    
#status: true if packet was rcvd successfully
#timestamp: time pkt was sent
#delay: rtt?
#tries: an array of (bitrate, nretries) 
def process_feedback(status, timestamp, delay, tries):
    global npkts, nsuccess, nlookaround, NBYTES, currRate, NRETRIES
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called
    for t in tries:
        (bitrate, nretries) = t
        nretries -= 1
        bitrate = common.RATES[bitrate][-1]/2.0
        
        br = rates[bitrate]
        br.tries = (br.tries + 1) % 10000
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
    for i, br in rates.items():
        p = br.success / br.tries
        br.succ_hist += br.success
        br.att_hist += br.tries
        rate.ewma.feed(timestamp, p)
        br.success = 0
        br.tries = 0
    self.last_update = timestamp

# thru = p_success * megabits_xmitted / time for 1 try of 1 pkt (in seconds?)
def throughput(psuccess, rtt, pktsize = NBYTES*8/1000000):
    global npkts, nsuccess, nlookaround, NBYTES, currRate, NRETRIES
    global bestThruput, nextThruput, bestProb, lowestRate, time_last_called
    
    return psuccess*pktsize/rtt
