<!-- -*- mode: markdown -*- -->

Data File Formats
=================

The folders `raw` and `data` contain captured bitrate traces.

Capturing traces
----------------

Traces can be captured with `collect.sh`.  This script restarts the driver, starts a packet-spewing script, captures a trace, and kills the packet source.  It has three arguments: an IP address to spew packets at, a file name to write the trace to, and how long to record the trace for.  For example

    ./collect.sh 10.0.0.1 test 60

would capture a 60-second trace to `raw/test.trace`, while sending a deluge of packets toward `10.0.0.1`.

Files `raw/*.trace`
-------------------

These are directly captured from the kernel, with newer versions; they have one record per line, such as:

    Last(2630707680) took 5135412 ns / 20 tries with rate 22 at 26000(24800) kbps [1]
    
There are six fields here:

 + A unique identifier based on the start time for transmission
 + The time it took to transmit the packet, in nanoseconds
 + The number of tries it took to transmit it (including the successful transmission), up to 20.
 + The identifier for the rate
 + The rate's kilobits per second
 + The rate's kilobits of payload per second; this elides the overhead of FEC and physical-layer headers.
 + The line's index in the internal kernel buffer; if this ever surpasses about 30, we might be missing records.
      
The `util/munge.py` script should be used to transform these files for the simulator, and really for any other purpose at all.

There are also sanity-check lines like

    0:46 1:323 2:5 3:9 4:13 5:76 6:169 7:739 8:228 9:100 10:290 11:3 
 
These are ignored by the munger, but if any numbers get appreciably big (compared to the range of an unsigned int), there may be problems.


Files `data/*.dat`
-------------------

These files are converted from the `raw2/*.trace` files into Python trace dumps.  They're best read with:

    eval(open(file_name, "rt").read())

Each file contains a tuple, with three entries: the start time of the first packet, the data arrays, and the start time of the last packet.  The data array has a list of tuples for each rate; thus, it is a list of 12 lists.

Each list of tuples has tuples of three elements: the send time, whether or not the packet succeeded, and how long the transmission took.  The tuples are ordered by send time.

