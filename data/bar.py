import numpy as np
import matplotlib.pyplot as plt

N = 4
samplerate1 = (16.474, 13.585, 5.42, 16.138, 7.455)
minstrel1 = (12.653, 10.208, 7.587, 10.867, 8.430)
minproved1 = (17.037, 14.879, 11.107, 15.846, 12.162)

samplerate2 = (13.107, 9.688, 7.982, 13.894)
minstrel2 = (11.575, 10.837, 8.320, 11.729)
minproved2 =(16.869, 15.156, 12.570, 16.292)



ind = np.arange(N)  # the x locations for the groups
width = 0.25       # the width of the bars

fig = plt.figure()
ax = fig.add_subplot(111)
sr1 = ax.bar(ind, samplerate2, width, color='r')
mn1 = ax.bar(ind+width, minstrel2, width, color='b')
mp1 = ax.bar(ind+2*width, minproved2, width, color='y')

# add some
ax.set_ylim([0,20])
ax.set_xlim([-0.5, 6])
ax.set_ylabel('Throughput in Mbps')
ax.set_xticks(ind+width+width)
ax.set_xticklabels( ('clear', 'moving', 'corner', 'interference') )

ax.legend( (mn1[0], sr1[0], mp1[0]), ('Minstrel', 'SampleRate', 'Minproved') )

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%r'% (round(height,1)),
                ha='center', va='bottom', rotation=60)

autolabel(mn1)
autolabel(sr1)
autolabel(mp1)

plt.show()
