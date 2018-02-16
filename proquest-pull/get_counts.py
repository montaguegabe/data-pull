from six.moves import cPickle as pickle
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
import numpy as np
from collections import OrderedDict
from operator import itemgetter

vocab = {}
with open('news_corpus.pickle', 'rb') as pf:
	articles = pickle.load(pf)
fdist = FreqDist()
for article in articles:
	for word in word_tokenize(article):
		fdist[word.lower()] += 1
total_count = fdist.N()
for word, count in fdist.items():
	vocab[word] = [count / float(total_count), 0]

with open('scientific_corpus.pickle', 'rb') as pf:
	articles = pickle.load(pf)
fdist = FreqDist()
for article in articles:
	for word in word_tokenize(article):
		fdist[word.lower()] += 1
total_count = fdist.N()
for word, count in fdist.items():
	old_entry = vocab[word] if word in vocab.keys() else [0, 0]
	old_entry[1] = count / float(total_count)
	vocab[word] = old_entry

def lam_fun(value):
	return value[1][0] + value[1][1]
sorted_words = sorted(vocab.items(), key=lam_fun, reverse=True)
with open('counts.pickle', 'wb') as pf:
	pickle.dump(sorted_words, pf)

# x = []
# y = []
# for thing in new_thing:
# 	x.append(thing[1][0])
# 	y.append(thing[1][1])
# plt.scatter(x, y, norm=True)
# plt.show()