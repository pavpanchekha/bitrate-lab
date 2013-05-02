# Colleen Josephson, 2013
# This file attempts to implement the minstrel rate control algorithm

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
        self.throughput = 0
        self.ewma_prob = 0 #current time weighted chance that pkt @ will arrive
        #success chance from the last time interval in which minstrel recorded data
        #Should there be no data, then the figure from the earlier time interval
        #(containing data) is used
        self.this_prob = 0 

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

#10 times a second (this frequency is alterable by changing the driver code) a timer
# fires, which evaluates the statistics table. EWMA calculations (described below) 
# are used to process the success history of each rate. On completion of the 
# calculation, a decision is made as to the rate which has the best throughput, 
# second best throughput, and highest probability of success. This data is used for 
# populating the retry chain during the next 100 ms. Note that the retry chain is 
# described below.
def apply_rate():
    #Minstrel spends a particular percentage of frames, doing "look around" i.e. 
    #randomly trying other rates, to gather statistics. The percentage of 
    #"look around" frames defaults to 10%. The distribution of lookaround frames is
    #also randomized somewhat to avoid any potential "strobing" of lookaround 
    #between similar nodes.
    pass

def process_feedback():
    pass

# thru = p_success * megabits_xmitted / time for 1 try of 1 pkt
def throughput():
    pass

# The EWMA calculation is carried out 10 times a second, and is run for each rate. 
# By "new results", we mean the results collected in the just completed 100 ms 
# interval. Old results are the EWMA scaling values from before the just completed 
# 100 ms interval.
def ewma():
    pass
