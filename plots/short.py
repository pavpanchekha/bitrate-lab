import matplotlib.pylab as plt
import numpy as np

mins = [7.74, 10.46, 8.66, 8.19, 10.22]
minp = [9.68, 15.74, 12.15, 12.35, 12.48]
samp = [8.86, 17.93, 9.01, 8.15, 4.98]

width = .35

fig = plt.figure()
ax = fig.add_subplot(111)
ind = np.arange(len(mins))
rects1 = ax.bar(ind, mins, width, color='r')
rects2 = ax.bar(ind + width, samp, width, color='y')

ax.set_ylabel("Throughput [Mbps]")
ax.set_title("Throughput versus length of trace")
ax.legend( (rects1[0], rects2[0]), ('Minstrel', 'SampleRate') )

ax.set_xticks(ind+width)
ax.set_xticklabels(("3s", "5s", "7s", "10s", "15s"))

ax.set_ylim((0.0, 20.0))

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height, str(round(height, 1)), ha='center', va='bottom')
        

autolabel(rects1)
autolabel(rects2)

plt.show()


