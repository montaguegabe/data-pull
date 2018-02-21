# Parameters
LOG_FNAME = 'mining.log'
DEFAULT_PAGESIZE = 25
OUT_DIR = 'data-html'

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

# Get keywords to extract
DEFAULT_KWS = ['climate', 'earth']
raw = raw_input('Which keywords? (sep. with comma, default: %s)' % ','.join(DEFAULT_KWS))
if len(raw) == 0:
    keywords = DEFAULT_KWS
else:
    keywords = raw.split(',')

# Get starting index
raw = raw_input('Enter starting index (default 1)')
record_index = None
if len(raw) == 0:
    record_index = 1
else:
    record_index = int(raw)

writelog('Searching with keywords %s, starting at index %d' % (keywords, record_index))

# Form query
import requests
search_include = map(lambda str2: 'cql.keywords any ' + str2, keywords)
search_filter = [
    # (We apply this filter to be able to get the full HTML of each)
    'dc.publisher=Nature Publishing Group'
]
cql_query = '(' + ' OR '.join(search_include) + ') AND ' + ' AND '.join(search_filter)
#print 'Query:', cql_query

url = 'http://api.nature.com/content/opensearch/request'

total_records = None

# Loop through pages
import requests
import os
while True:
    data = {
        'httpAccept': 'application/json',
        'queryType': 'cql',
        'startRecord': str(record_index),
        'query': cql_query
    }
    response = requests.get(url, params=data)
    body = response.json()

    if total_records == None:
        total_records = body['feed']['sru:numberOfRecords']
        writelog('Found a total of %d records' % (total_records))

    # Process each entry
    entries = body['feed']['entry']
    for entry in entries:
        doi = entry['id']
        writelog('Downloading DOI: %s' % doi)

        entry_url = entry['link']

        # Get the redirected page
        response = requests.get(entry_url)
        redirected_url = response.url

        # Build the URL of the HTML page with the full article
        doc_id = redirected_url.split('/')[-1]
        article_url_fmt = 'http://www.nature.com.ezp-prod1.hul.harvard.edu/articles/%s'
        article_url = article_url_fmt % doc_id
        
        cookies = util.get_cookies('../credentials/gabe_nature.json')
        article_fname = util.download_file(article_url, cookies, prefix=OUT_DIR + '/')

        # Check if something went wrong
        ext = article_fname.split('.')[-1]
        if ext == 'pdf' or ext == 'html':
            writelog('Detected error, deleting..')
            os.remove(OUT_DIR + '/' + article_fname)


    # Check if we should exit
    if body['feed']['opensearch:itemsPerPage'] < DEFAULT_PAGESIZE:
        break

    # Set the next record index
    record_index = int(body['feed']['sru:nextRecordPosition'])
    writelog('Record index: %d' % record_index)

writelog('Query download completed')

