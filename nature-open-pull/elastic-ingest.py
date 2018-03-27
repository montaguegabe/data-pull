# We wish to upload JSON files to elastic
# NOTE: Majority of this file is copied from extract.py

# Parameters
LOG_FNAME = 'elastic-ingest.log'
INPUT_PATH = './data-html/'
REVISION_NUM = 1
NUM_CHUNKS = 2048

from os import listdir
from os.path import isfile, join
import re

file_list = [f for f in listdir(INPUT_PATH) if isfile(join(INPUT_PATH, f))]
chunk_size = int(len(file_list) / NUM_CHUNKS) + 1
chunks = [file_list[i:i + chunk_size] for i in xrange(0, len(file_list), chunk_size)]
print('MAX_CHUNK: %d' % len(chunks))

START_CHUNK = int(raw_input('START_CHUNK: '))
END_CHUNK = int(raw_input('END_CHUNK: ')) # (exclusive)
OUT_DIR = './data-doc/' # For output pickle files

# Give access to utils
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import util

# Set up logging
import datetime
log = open(LOG_FNAME, 'a')
def writelog(str2):
    print str2
    log.write(datetime.datetime.now().isoformat() + ': ' + str2 + '\n')

writelog('Starting Elasticsearch ingestion...')
writelog('START_CHUNK: ' + str(START_CHUNK))
writelog('END_CHUNK: ' + str(END_CHUNK))

# We define a method that turns HTML into text
# Source: https://stackoverflow.com/questions/328356/extracting-text-from-html-file-using-python
def html2txt(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Kill all script, style, and link elements
    for script in soup(['script', 'style', 'a', 'h2']):
        script.extract()    # rip it out
        
    # Get text
    text = soup.get_text()

    return text

def is_number(s):
    return s[0].isdigit()

# Certain sections contain useless information
skip_sections = set([
    'acknowledgements',
    'references',
    'author-information',
    'supplementary-information',
    'article-comments'
])

# Does preprocessing on a file and returns status
from bs4 import BeautifulSoup
import re
import dateutil.parser

def fileToDocs(fname):
    try:

        docs_return = []

        html = None
        with open(INPUT_PATH + fname, 'r') as example_html:
            html = example_html.read()

        soup = BeautifulSoup(html, 'html.parser')

        # Find article date and title
        date_el = soup.find('time')
        title_el = soup.find('h1', {'data-article-title': re.compile(r".*")})
        title = html2txt(str(title_el))
        date_str = html2txt(str(date_el))
        try:
            date = dateutil.parser.parse(date_str)
        except Exception as e:
            date = None

        # Find article sections
        sections = soup.findAll('section', {'aria-labelledby': re.compile(r".*")})

        # Extract each to text
        #section_texts = []
        #section_titles = []
        s_count = 0
        for section in sections:
            
            # Skip useless sections
            s_title = section['aria-labelledby']
            if s_title in skip_sections:
                continue
            
            # Otherwise we turn the section into plain text
            text = html2txt(unicode(section))
            text = re.sub(r'[^\x00-\x7f]',r' ', text) # remove non-unicode
            #section_texts.append(text)
            #section_titles.append(s_title)
            s_count += 1

            # Create doc
            doc = {}
            doc['article_title'] = title
            doc['article_date'] = date
            doc['section_title'] = s_title
            doc['text'] = text
            docs_return.append(doc)

    except Exception as e:
        return (e, [])
    else:
        return (None, docs_return)

# Turns a chunk of files into docs
def filesChunkToDocs(chunk):
    docs = []
    errors = []
    for file2 in chunk:
        (err, docs_small) = fileToDocs(file2)
        errors.append(err)
        docs.extend(docs_small)

    return (errors, docs)

from elasticsearch import Elasticsearch
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk

# Turns a chunk of files into docs while bulk ingesting
def filesChunkToDocsIngest(chunk):

    # Set up ES
    host = 'search-e5ud2nsmhsp52orvyvpqur0k09x-bkkbyr2hfjeiyujryuqkm5y3hu.us-east-1.es.amazonaws.com'
    es = Elasticsearch(
        hosts=[{'host': host, 'port': 443}],
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    es.info()

    docs = []
    errors = []
    for file2 in chunk:
        (err, docs_small) = fileToDocs(file2)
        errors.append(err)
        docs.extend(docs_small)

    # Ingest all docs
    resp = bulk(es, docs, stats_only=True, index='nature-english', doc_type='section')

    return (errors, docs, resp)

#print 'Chunks:'
#for chunk in chunks:
#    print len(chunk)

target_chunks = chunks[START_CHUNK:END_CHUNK]

# Map
from joblib import Parallel, delayed
import multiprocessing

num_cores = multiprocessing.cpu_count()
print 'Cores:', num_cores
results = Parallel(n_jobs=num_cores)(delayed(filesChunkToDocsIngest)(i) for i in target_chunks)

# Reduce while writing errors
#doc_list = []
for result in results:
    (errors, docs, resp) = result
    writelog('Success/failure: (%d, %d)' % (resp[0], resp[1]))
    """
    for i in xrange(len(docs)):
        err = errors[i]
        #doc = docs[i]
        if err:
            writelog(str(err))
        #doc_list.append(doc)
    """

# Pickle
#import cPickle as pickle
#pickle.dump(doc_list, open(OUT_DIR + 'doc%d-%d-%d.p' % (REVISION_NUM, START_CHUNK, END_CHUNK), 'wb'))

writelog('Ingestion complete')
