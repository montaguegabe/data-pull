import matplotlib.pyplot as plt
from six.moves import cPickle as pickle
import numpy as np

with open('counts.pickle', 'rb') as pf:
    sorted_words = pickle.load(pf)

# # Option A: freq. in x vs freq. in y
x = []
y = []
max_count = 1000
to_look = sorted_words[0:max_count - 1]
for entry in to_look:
	x.append(entry[1][0])
	y.append(entry[1][1])
x = np.array(x)
y = np.array(y)
x = np.power(x, 1/4)
y = np.power(y, 1/4)
x /= max(x)
y /= max(y)
plt.plot(x, y, 'o')
plt.plot([0,1],[0,1], 'k-')
plt.axis('equal')
plt.axis([0, 1, 0, 1])
plt.title('Word Frequencies in Scientific and Newspaper Corpuses')
plt.xlabel('Frequency in Newspapers (normalized)')
plt.ylabel('Frequency in Scientific Journals (normalized)')
plt.savefig('versionA.png')
plt.show()

# Option B: relative vs. overall frequencies
x = []
y = []
max_count = 1000
to_look = sorted_words[0:max_count - 1]
counter = max_count
for entry in to_look:
    v_freq = entry[1][0]
    s_freq = entry[1][1]
    x.append(v_freq / (v_freq + s_freq))
    y.append(float(counter))
    counter -= 1
x = np.array(x)
y = np.array(y)
y /= max(y)
plt.plot(x, y, 'o')
plt.title('Relative and Overall Word Frequencies')
plt.xlabel('Relative Frequency (1 found only in newspapers, 0 found only in scientific literature)')
plt.ylabel('Overall frequency (1 is most common, 0 is least common)')
plt.plot([.5,.5],[0,1], 'k-')
plt.axis('equal')
plt.axis([0, 1, 0, 1])
plt.savefig('versionB.png')

plt.show()