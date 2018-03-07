import pickle
from gensim.models import word2vec
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

model = word2vec.Word2Vec.load('word2vec_queries.m')
vocab = list(model.wv.vocab)

X = pickle.load(open('X_tsne_simple.p', 'rb'))


plt.scatter(X[:, 0], X[:, 1])
for label, x, y in zip(vocab, X[:, 0], X[:, 1]):
    plt.annotate(label, xy=(x, y), xytext=(0, 0), textcoords='offset points')
plt.show()