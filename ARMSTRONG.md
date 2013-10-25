<!-- -*- mode: markdown -*- -->

The Design of Armstrong
=======================

Armstrong is a new bitrate adaptation protocol.  In simulations,
Armstrong achieves 91% of the maximum throughput, which is
an almost 25% improvement on existing algorithms like Minstrel and
SampleRate.  This document explains the design of Armstrong.

Armstrong's exact behavior is best understood by reading the source
code, which can be found in `pysim/armstrong.py`; the code is simple
and easy to digest.  This document does not attempt to exhaustively
document it, but instead tease a few general ideas out of Armstrong's
design.

# Overview

Armstrong is similar to Minstrel and SampleRate in that it balances
*sampling* bitrates that don't appear very good with *using* bitrates
that appear good.  In broad strokes, there are two questions Armstrong
must answer:

 + How to estimate the quality of a bitrate

 + When to sample and when to use

Armstrong estimates bitrate quality from an EWMA measuring that
bitrate's probability of success. Each bitrate is sampled at a
different rate; rates that change in relative importance more often
are sampled more frequently.

# Bitrate quality

The quality of a bitrate is inversely related to its expected
transmission time.  The expected transmission time is computed based
on its probability of success with

    def tx_time(r, prob, nbytes):
        txtime = tx_lossless(r, nbytes)
        score = 0
        likeliness = 1
    
        if prob == 0: return float('inf')
    
        for i in range(0, backoffs(r)):
            score += likeliness * prob * (txtime + difs(r))
            txtime += txtime + backoff(r, i + 1)
            likeliness *= (1 - prob)
    
        score += likeliness * ((txtime + difs(r)) + \
                               (txtime + backoff(r, i+1)) / prob)
    
        return score

In the code above, `backoffs(r)` denotes the number of backoff times
possible for a rate (it is 7 for 802.11g rates and 6 for 802.11b
rates); `backoff(r, n)` is the length of the `n`th backoff period;
`difs(r)` is the size of the DCF Interframe Space for a rate; and
`tx_lossless(r, l)` is the lossless transmission time if the packet
can be assumed to succeed.  All times are in nanoseconds.  The
lossless transmission time can be computed with:

    def tx_lossless(rix, nbytes):
        bitrate = rates.RATES[rix].mbps
        version = "g" if rates.RATES[rix].phy == "ofdm" else "b"
        sifs = 10 if version == "b" else 9
        ack = 304 # Somehow 6mb acks aren't used
        header = 192 if bitrate == 1 else 96 if version == "b" else 20
        return (sifs + ack + header + (nbytes * 8 / bitrate)) * 1000

Note that this computation includes backoff, headers, the SIFS and
DIFS, and the time to receive an acknowledgment (or determine that
none was sent).

# Probability Estimation

The bitrate quality estimation requires knowing the probability that a
packet will be successfully transmitted.  This must be estimated.
Armstrong uses an exponentially-weighted moving average to estimate
the success probability.  This EWMA is fed zeros for every packet that
failed to transmit successfully and ones for every packet that
successfully transmitted.

# EWMA Weighting

Armstrong weights sample packets and use packets differently.  This
avoids problems evident in Minstrel, which can take many hundreds of
milliseconds to react to a failing bitrate.  Sample packets are
weighted relative to the "normal sampling rate", which is 10
milliseconds.  Use packets are weighted relative to the lossless
transmission time for 10 packets at that bitrate.  In both cases, the
EWMA weight is the time since the last such packet (at that rate and
also use or sample) divided by the benchmark time.

# When to Sample

Each bitrate maintains a sampling rate, its expected time between
sample packets.  Each bitrate also schedules a sampling packet between
half and three halves of the sampling rate from the last sampling
packet.  If any bitrate is scheduled to send a sample packet,
Armstrong sends a sampling packet at that bitrate; otherwise it sends
a use packet.  If multiple bitrates would like to send a sampling
packet, Armstrong chooses one rate uniformly at random.

# Choosing the Sampling Rate

The sampling rate is based on the expected time between sort order
changes.  Imagine sorting the bitrates in increasing order of expected
transmission time.  When a packet is sent, the probability estimate of
the bitrate it was sent at may change, and thus the expected
transmission time may also change.  This may move the bitrate up or
down in the sorted sequence of bitrates.  If the bitrate was among the
top four bitrates before the move, this is termed a *sort-order
change*.  Armstrong maintains the sampling rate as an
exponentially-weighted moving average of the frequency of sort-order
changes times a multiplier; the multiplier varies exponentially with
the position of the rate in the sorting order.  No sample rate is
allowed to increase beyond two seconds (a cutoff inspired by
Minstrel).  When a bitrate is the best bitrate, and thus the bitrate
used by use packets, its sampling rate is reset to the "normal
sampling rate" of 10 milliseconds.

# Why is Armstrong Better?

Armstrong has a few core ideas that improve on previous algorithms:

 + Accurate transmission time estimation. Previous algorithms got this
   wrong or took shortcuts; it turns out that if you're optimizing for
   the wrong thing, it doesn't matter how close you get.
   
 + Sampling rates that are worse than the current one.  One day the
   current rate will no longer be the best rate, and on that day you
   will want to know which rate is second-best.
   
 + Tuning each rate's sampling rate.  Rates that never work should be
   infrequently sampled; Armstrong solves this with an algorithm based
   on sort order changes.

These three ideas form the core of Armstrong and, in fact, Armstrong
more or less lacks other ideas at all.
