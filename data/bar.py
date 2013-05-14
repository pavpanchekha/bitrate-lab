import numpy as np
import matplotlib.pyplot as plt

N = 12
throughput = (.806, 1.632, 4.716, 5.118, 7.888, 8.784, 9.865, 15.156, 1.174, 1.960, 0, 1.189)

ind = np.arange(N)  # the x locations for the groups
width = 0.5       # the width of the bars

fig = plt.figure()
ax = fig.add_subplot(111)
rects1 = ax.bar(ind, throughput, width, color=['red', 'orange', 'DarkGoldenRod', 'yellow', 'lawngreen', 'DarkGreen', 'blue', 'DarkBlue', 'indigo',  'purple', 'DarkMagenta', 'gray'] )

# add some
ax.set_ylim([0,17])
ax.set_xlim([-0.5, 12])
ax.set_ylabel('Throughput in Mbps')
ax.set_title('Throughput for Constant Bitrate')
ax.set_xticks(ind+width)
ax.set_xticklabels( ('1', '2', '5.5', '6', '9', '11', '12', '18', '24', '36', '48', '54') )

#ax.legend( (rects1[0], rects2[0]), ('Men', 'Women') )

def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*height, '%r'% (height),
                ha='center', va='bottom')

autolabel(rects1)


plt.show()
