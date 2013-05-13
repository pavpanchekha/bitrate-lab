
import numpy
import collections
import re
import sys

FIELDS = ["ts", "delay", "tries", "rateid", "kbps", "user_kbps", "i"]
Record = collections.namedtuple("Record", FIELDS)

NUM_RATES = 24

LINE_RE = r"""Last\((\d+)\) took (\d+) ns / (\d+) tries with rate (\d+) at (\d+)\((\d+)\) kbps \[(\d+)\]\n"""
LINE_RE = re.compile(LINE_RE)
def parse_line(lines):
    for line in lines:
        match_info = LINE_RE.match(line)
    
        if not match_info:
            print(ValueError("Cannot parse line", line))
        else:
            yield Record(*map(int, match_info.groups()))

def clean_up(record_stream):
    prev = next(record_stream)
    yield prev

    for record in record_stream:
        # The kernel sets:
        #   ts and rateid, kbps, user_kbs
        # then it sends the packet
        # then it sets:
        #   delay, tries
        # So we uniquify by the delay, which should be unique
        if record.delay != prev.delay and record.rateid != prev.rateid and record.ts != prev.ts:
            yield record
            prev = record

def numpyify(record_stream):
    array = [[(0,0)] * NUM_RATES]

    for record in record_stream:
        idx = record.rateid

        if array[-1][idx] != (0, 0):
            array.append([(0, 0)] * NUM_RATES)

        array[-1][idx] = (record.delay, record.tries)

    return numpy.array(array)

def save(array):
    numpy.save(OUTFILE, array)

def pipe(val, *fns):
    for fn in fns:
        val = fn(val)
    return val

OUTFILE = None

if __name__ == "__main__":
    OUTFILE = open(sys.argv[1], "wb")
    pipe(sys.stdin,
         parse_line,
         clean_up,
         numpyify,
         save)
