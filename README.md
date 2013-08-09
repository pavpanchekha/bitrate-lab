<!-- -*- mode: markdown -*- -->

Bitrate Selection Laboratory
============================

This suite of code provides a way to test bit-rate selection algorithms on real-world data.  It includes both a mechanism to capture the performance of various bitrates, and a way to run bit-rate selection algorithms on the resulting data.  The simulation provides repeatable results and rapid development; the capture tools allow real-world data to be used throughout.

This set of tools was written by Colleen Josephson and Pavel Panchekha in the spring of 2013 for Hari Balakrishnan's 6.829 class at MIT.  The code is provided under the MIT license; a copy should be available in `LICENSE.md`.

Collecting traces
-----------------

Traces can be collected from any consumer laptop that uses the `ath9k` Linux module for wireless communication.  A modified version of this driver, located in the `ath9k/` folder, allows data collection by choosing a bit rate at random for each packet and recording the success or failure of the packet transmission.  Bit rates are chosen to sample equally in time, including retransmissions; thus very high bitrates are often lightly sampled, since they are much more likely to involve retransmissions.

Traces are collected by running the `collect.sh` script, which takes three parameters: an IP address to flood packets at (usually the router's IP address), a file name to send to (`test` is a good choice if you don't want to keep the data around), and the duration (in seconds) for which to capture the trace. For example, you might capture data by running

    ./collect.sh 10.0.0.1 test 60

Simulating algorithms
---------------------

Once a trace is captured, it can be used to run various bitrate selection algorithms and compare the results.  The main entry point is the `harness.py` file, which requires an algorithm to run and a trace to run the algorithm against.  For example,

    pypy harness.py samplerate ../data/test.dat

will execute the SampleRate algorithm against the test data gathered in the previous section.  Using PyPy is recommended, since the simulation is CPU-intensive and since Python is not a particularly fast language.  Implementations of the SampleRate and Minstrel algorithms are provided, along with a research prototype named `p92`, which is a simple but very fast bitrate adaptation algorithm.  A comprehensive list of provided algorithms is:

 + `constant`: Always uses a constant bitrate; use the `RATE` environment variable to control which.
 + `samplerate`: The SampleRate algorithm, as described in John Bicket's thesis.
 + `minstrel`: The Minstrel algorithm, as found in Linux 3.10.5.
 + `p92simple` : A very simple but consistently-decent algorithm based on a few simple ideas.  Also a building block for `p92`
 + `p92` : A very good rate control algorithm, usually achieving approximately 90% of optimal performance.
 + `optimal` : Examines the full data set to always act optimally; used as a benchmark.

Writing algorithms
------------------

It is relatively easy to write a new bitrate selection algorithm and test it.  As more common code is written, it should only get easier.  A bitrate selection algorithm is a Python module that provides two methods: `apply_rate` and `process_feedback`.

`apply_rate` receives one argument, the current simulation time.  It must return a multi-rate retry chain as a list of 2-tuples, each naming a rate and the maximum number of times to attempt that rate.  The rate is named by an index into `common.RATES`; indices 0 through 3 name 802.11b rates in order of increasing bitrates, and indices 4 through 11 name the additional 802.11g rates, also in order of increasing bitrate.

`process_feedback` receives four arguments: whether or not the packet send succeeded; the simulation time; the time to send (or not) the packet; and the number of attempts made at each rate as a multi-rate retry chain similar in format to the output of `apply_rate`.

`constant.py` can serve as a simplistic model of how to write a selection algorithm.  It is somewhat over-complicated to provide a model of how to actually write a rate-control algorithm.  `p92simple.py` is an algorithm based on this model that is very simple is thus also a good model.

What are the folders?
---------------------

 + `ath9k/`: modified network driver used to collect traces
 + `util/`: scripts to collect traces
 + `raw/`: raw trace data; see `DATA.md`
 + `data/`: parsed trace data; see `DATA.md`
 + `pysim/`: Python simulation framework, including bit rate algorithms
 + `out/`: output of the algorithms on our traces
 + `plots/`: pretty plots generated from the data
 + `paper/`: writeup of the basic approach and the results
