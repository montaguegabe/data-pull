# Parameters
LOG_FNAME = 'extract.log'
INPUT_PATH = './data-html/'

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

# Get starting index
out_dir = raw_input('Preprocessing directory name (must be created already): ')

writelog('Starting preprocessing to %s' % out_dir)

from os import listdir
from os.path import isfile, join
import re

file_list = [f for f in listdir(INPUT_PATH) if isfile(join(INPUT_PATH, f))]

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
import cPickle as pickle
def fileToStatus(fname):

    try:
        html = None
        with open(INPUT_PATH + fname, 'r') as example_html:
            html = example_html.read()

        soup = BeautifulSoup(html, 'html.parser')

        # Find article sections
        sections = soup.findAll('section', {'aria-labelledby': re.compile(r".*")})

        # Extract each to text
        section_texts = []
        s_count = 0
        for section in sections:
            
            # Skip useless sections
            s_title = section['aria-labelledby']
            if s_title in skip_sections:
                continue
            
            # Otherwise we turn the section into plain text
            text = html2txt(unicode(section))
            text = re.sub(r'[^\x00-\x7f]',r' ', text) # remove non-unicode
            section_texts.append(text)
            s_count += 1

        # Split the string by space first
        texts_word_lists = []
        for text in section_texts:
            text_list = text.split(' ')
            text_list_out = []
            for word in text_list:
                if not word:
                    continue
                elif is_number(word):
                    text_list_out.append('TOKEN_NUMBER')
                else:
                    subwords = re.split('[^a-zA-Z]', word)
                    for word in subwords:
                        if word != '':
                            text_list_out.append(word.lower())

            texts_word_lists.append(text_list_out)
            
        prefix = out_dir + '/' if out_dir[-1] != '/' else out_dir
        pickle.dump(texts_word_lists, open(prefix + fname + '.p', 'wb'))

    except Exception as e:
        return 'File %s processed. ERROR: %s' % (fname, str(e))
    else:
        return 'File %s processed. Found %d sections' % (fname, s_count)



import multiprocessing
pool = multiprocessing.Pool()
statuses = pool.map(fileToStatus, file_list)

for status in statuses:
    writelog(status)

writelog('Preprocessing completed to directory %s' % out_dir)

