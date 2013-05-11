# This file is meant to be loaded from a iPython shell; run
#
#   %load explore.py
#
# to load it, then load a data file with
#
#   init("file.dat")

start = 0
data = [[] for i in range(12)]
end = 0

npkts = 0

def init(fn):
    global start, data, end, npkts
    start, data, end = eval(open(fn, "rt").read())

    npkts = sum(len(rdata) for rdata in data)

def cum(s):
     i = 0
     for v in s:
         i += v
         yield i

def rate_cdf(rate):
    xs, ys = zip(*map(lambda x: x[:2], data[rate]))
    return array(xs), array(list(cum(ys)))

def plot_rates():
    for i in range(len(data)):
        plot(*rate_cdf(i))
