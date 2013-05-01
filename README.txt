
Data File Formats
=================

The folders `raw` `data` contains captured bit rate success traces.

Files `raw/*.trace`
-------------------

These are directly captured from the kernel; they have one record per line, such as:

    Last(2630707680) took 5135412 ns / 20 tries with rate 22 at 26000(24800) kbps
    
There are six fields here:

 + A unique identifier based on the start time for transmission
 + The time it took to transmit the packet, in nanoseconds
 + The number of tries it took to transmit it (including the successful transmission), up to 20.
 + The identifier for the rate
 + The rate's kilobits per second
 + The rate's kilobits of payload per second; this elides the overhead of FEC and physical-layer headers.
 
The last line of each file may be incomplete.  The records may also be muddled with concurrency errors and partial reads.  It is suggested that the `data/numpyify.py` script be used to transform these files before use.

Files `data/*.npy`
------------------

These files are converted from the above into Numpy array dumps.  They're best read with:

    data = numpy.load([file_object or file_name])

Each file stores one array, which has dimensions N by 24 by 2.  Each row denotes a point in time (loosely); each column denotes a bit rate.  Each pair of these has both a time (in nanoseconds) and a number of tries; they can be extracted as:

    delay = data[t, rate, 0]
    tries = data[t, rate, 1]
    
Some entries of this array claim to have zero tries that took zero nanoseconds.  These in fact denote missing data; missing data is best detected with:

    if data[t, rate].any():
        ...

