import csv
from six.moves import cPickle as pickle
import string
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import re

MIN_LENGTH = 700
FL_CUTOFF = 40

articles = []

spam_markers = ["Guest", "@", "Follow us", "donate", "Donate", "Kickstarter", "Subscribe"]
csv.field_size_limit(290000)

utc = pytz.UTC
# When this data was collected
collection_start = utc.localize(datetime(2016, 10, 26))
collection_end = utc.localize(datetime(2016, 11, 25))

def has_spam(row):
    for spam in spam_markers:
        if spam in row:
            return True
    return False

def is_comments(text):
    lines = text.split('\n')
    comments = 0
    for line in lines:
        # Comments in this file are formatted as "blah blah blah" name
        if len(line) > 0 and line[-1] not in string.punctuation:
            comments += 1
    # If > 1/2 of lines end without punctuation, it's probably a thread
    if comments > (len(lines) / 2):
        return True
    return False

def remove_urls(text):
    index = text.find('http://')
    while (index > -1):
        end = text.find(' ', index)
        text = text[0:index] + text[end:]
        index = text.find('http://')
    return text

def remove_labels(text):
    # If first line is very short, it's probably "0 comments" or "Print"
    first_line =  text[0:FL_CUTOFF].find("\n")
    if first_line > -1:
        text = text[first_line + 1:]
    return text

def remove_unreadable(text):
    # Removes text in the '/X..' format that is probably an xml artifact
    return re.sub('\\\\x..','',text)

with open('real.csv', 'rt', encoding='utf8') as csvfile:
    with open('test_output.txt', 'w+', encoding='utf8') as outfile:
        titles = []
        reader = csv.reader(csvfile)
        count = 0
        for row in reader:
            try:
                [title, text] = row
            except:
                continue
            if title != "" and title != "title" and title not in titles:
                text = text.encode('utf-8').decode('utf-8', 'ignore')
                titles.append(title)
                count += 1
                text = remove_urls(text)
                text = remove_labels(text)
                text = remove_unreadable(text)
                text = BeautifulSoup(text, 'lxml').get_text()
                articles.append(text)
                outfile.write(text)

with open('news_corpus.pickle', 'wb') as pf:
    pickle.dump(articles, pf)
