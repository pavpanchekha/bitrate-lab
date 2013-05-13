
import numpy
import collections
import re
import sys

FIELDS = ["ts_s", "ts_ns", "delay", "tries", "rateid", "kbps", "user_kbps", "i"]
Record = collections.namedtuple("Record", FIELDS)

NUM_RATES = 12

LINE_RE = r"""Last\((\d+)\.(\d+)\) took (\d+) ns / (\d+) tries with rate (\d+) at (\d+)\((\d+)\) kbps \[(\d+)\]\n"""
LINE_RE = re.compile(LINE_RE)
def parse_line(lines):
    for line in lines:
        match_info = LINE_RE.match(line)
    
        if not match_info:
            print(ValueError("Cannot parse line", line))
        else:
            yield Record(*map(int, match_info.groups()))

def ts(record):
    return int(record.ts_s*1e9 + record.ts_ns)

def tuplify(record_stream):
    fst = next(record_stream)
    start = ts(fst)

    end = None
    rates = [[] for i in range(NUM_RATES)]
    rates[fst.rateid].append((start, fst.tries == 1, fst.delay))
    for r in record_stream:
        end = ts(r)
        rates[r.rateid].append((end, r.tries == 1, r.delay))

    return (start, rates, end)

def save(data):
    with OUTFILE:
        OUTFILE.write(repr(data))

def pipe(val, *fns):
    for fn in fns:
        val = fn(val)
    return val

OUTFILE = None

if __name__ == "__main__":
    OUTFILE = open(sys.argv[1], "wt")
    pipe(sys.stdin,
         parse_line,
         tuplify,
         save)
