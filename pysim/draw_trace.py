import pylab
import numpy
import math
import sys
import os
import matplotlib.cm as cm
import matplotlib.ticker as ticker
import rates
import harness
import random

perm = {info.code: i for i, info in
        enumerate(sorted(rates.RATES, key=lambda info: info.mbps))}
rperm = {i: info.code for i, info in
         enumerate(sorted(rates.RATES, key=lambda info: info.mbps))}

def badness(rix, prob):
    txtime = harness.tx_time(rix, 1500)
    score = 0
    likeliness = 1
    for i in range(0, 10):
        score += likeliness * prob * (txtime + harness.difs(rix))
        txtime += txtime + harness.backoff(rix, i + 1)
        likeliness *= (1 - prob)
    score += likeliness * (txtime + harness.difs(rix))
    return score

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("USAGE: python draw_trace.py <datafile> [log]")
        exit()

    datfile = sys.argv[1]
    title = "Bitrate plot from {}".format(os.path.basename(datfile))
    dat = eval(open(datfile, "rt").read())

    start, data, end = dat
    secs = (end - start) / 1e9

    width = math.ceil(secs)
    harness.WINDOW = (end - start) / width
    img = numpy.zeros((len(data), width))
    best = numpy.zeros(width)

    idx = [0] * len(data)

    for i in range(0, width):
        t = (i + .5) / width * (end - start) + start
        ps = [harness.packet_stats(data, t, r) for r, _ in enumerate(data)]
        badnesses = [badness(rix, p) / 1e6 for rix, p in enumerate(ps)]

        best[i] = perm[numpy.argmin(badnesses)]
        for j, p in enumerate(ps):
            img[perm[j], i] = p

    fig, ax = pylab.subplots()

    ax.set_xlim(0, secs)
    ax.set_ylim(-.5, 11.5)
    ax.set_xlabel("Time (s)")

    # Hide the right and top spines
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Label each bitrate
    locator = ticker.MultipleLocator()
    ax.get_yaxis().set_major_locator(locator)

    def y_formatter(y):
        idx = rperm[round(y)]
        info = rates.RATES[idx]
        mbps = int(info.mbps) if info.mbps.is_integer() else info.mbps
        return "{} Mb/s".format(mbps)
    ax.fmt_xdata = lambda x: "{:.1f}s".format(x)
    ax.fmt_ydata = y_formatter

    ax.imshow(img, cmap=cm.Blues, interpolation='nearest', aspect="auto",
              extent=(0, secs, 11.5, -.5))
    ax.plot(numpy.arange(width) * secs / width, best, 'g', linewidth=2)

    labels = [y_formatter(i) for i, r in enumerate(rates.RATES)]
    formatter = ticker.FixedFormatter(['-'] + labels)
    ax.get_yaxis().set_major_formatter(formatter)

    if len(sys.argv) > 2:
        alpha = .5 ** (secs / 256)

        alg, log = eval(open(sys.argv[2], "rt").read())
        title = "{}, simulation of \"{}\"".format(title, alg)
        good_x = [(t - start) / 1e9
                  for t, rix, stat in log if stat]
        good_y = [perm[rix] + .4*random.random() - .2
                  for t, rix, stat in log if stat]
        bad_x  = [(t - start) / 1e9
                  for t, rix, stat in log if not stat]
        bad_y  = [perm[rix] + .4*random.random() - .2
                  for t, rix, stat in log if not stat]
        ax.plot(good_x, good_y, 'yo', alpha=alpha)
        ax.plot(bad_x, bad_y, 'ro', alpha=alpha)

    ax.set_title(title)
    pylab.show()
