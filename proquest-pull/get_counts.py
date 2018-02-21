from six.moves import cPickle as pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

tfidf_vectorizer = TfidfVectorizer(stop_words='english')
count_vectorizer = CountVectorizer(stop_words='english')
sci_vectorizer = CountVectorizer(stop_words='english')
news_vectorizer = CountVectorizer(stop_words='english')
sci2 = CountVectorizer(stop_words='english', max_features=100)
news2 = CountVectorizer(stop_words='english', max_features=100)

with open('news_corpus.pickle', 'rb') as pf:
    news_articles = pickle.load(pf)

with open('scientific_corpus.pickle', 'rb') as pf:
    sci_articles = pickle.load(pf)

tfidf_vectorizer.fit(news_articles + sci_articles)
cv_fit = count_vectorizer.fit_transform(news_articles + sci_articles)
counts = cv_fit.toarray().sum(axis=0)
sci_fit = sci_vectorizer.fit_transform(sci_articles)
sci_counts = sci_fit.toarray().sum(axis=0)
sci_total = sum(sci_counts)
news_fit = news_vectorizer.fit_transform(news_articles)
news_counts = news_fit.toarray().sum(axis=0)
news_total = sum(news_counts)

sci2.fit(sci_articles)
news2.fit(news_articles)

idf = tfidf_vectorizer.idf_

# Make CSV: word (label), total freq (size), rank (y), relative freq (x), sci. freq(detail), news freq(detail)
import csv

with open('tfidf_freqs.csv', 'w+', encoding='utf-8') as csvfile:
    fieldnames = ['word', 'total freq', 'idf', 'relative freq', 'sci. freq', 'news freq']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for word in {**sci2.vocabulary_, **news2.vocabulary_}:
        index = count_vectorizer.vocabulary_.get(word)
        n_index = news_vectorizer.vocabulary_.get(word)
        s_index = sci_vectorizer.vocabulary_.get(word)
        s_freq = 0 if s_index is None else sci_counts[s_index] / float(sci_total)
        n_freq = 0 if n_index is None else news_counts[n_index] / float(news_total)
        relative_freq = (n_freq / (n_freq + s_freq))
        total_freq = n_freq + s_freq
        writer.writerow({'word': word, 'total freq': total_freq, 'idf': idf[index],
                         'relative freq': relative_freq, 'sci. freq': s_freq, 'news freq': n_freq})
