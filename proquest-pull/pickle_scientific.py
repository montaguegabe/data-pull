import csv
from six.moves import cPickle as pickle
import string
from datetime import datetime
import pytz
from bs4 import BeautifulSoup
import os
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

def oneLiners(text):
    # If first line is very short, it's probably "0 comments" or "Print"
    text = re.sub("\n.\n", "\n", text)
    return text

def remove_unreadable(text):
    # Removes text in the '/X..' format that is probably an xml artifact
    return re.sub('\\\\x..','',text)

# Some of the articles have post date, which is not relevant
def remove_dates(text):
    matches = datefinder.find_dates(text, index=True)
    num_removed = 0
    for (date, (start, end)) in matches:
        if date.tzinfo is None:
            date = utc.localize(date)
        # Because datefinder is a bit messed up
        try:
            date > collection_start
        except:
            continue
        if date > collection_start and date < collection_end:
            text = text[0:start - num_removed] + " " + text[end - 1 - num_removed:]
            num_removed += end - start - 2
    return text



with open('scientific_test_output.txt', 'w+', encoding='utf8') as outfile:
    titles = []
    count = 0
    for txt in os.listdir("./scientific/"): #iterate through pdfs in pdf directory
        fileExtension = txt.split(".")[-1]
        if fileExtension != "txt":
            continue
        text = ""
        with open("./scientific/" + txt, 'r', encoding='utf8') as infile:
            for line in infile:
                if len(line) > 6:
                    text = text + line
        text = text.encode('utf-8').decode('utf-8', 'ignore')
        count += 1
        # text = remove_dates(text)
        text = remove_urls(text)
        text = oneLiners(text)
        text = remove_unreadable(text)
        text = BeautifulSoup(text, 'lxml').get_text()
        articles.append(text)
        outfile.write(text)

with open('scientific_corpus.pickle', 'wb') as pf:
    pickle.dump(articles, pf)
