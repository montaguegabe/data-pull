# source: https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py

import requests
import re

import json
def get_cookies(fname):
    with open(fname, 'r') as f:
        json_str=f.read().replace('\n', '')

    return json.loads(json_str)

def download_file(url, cookies):

    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, cookies=cookies, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

def find_between(str2, before, after):

    result = re.search(before + '(.*)' + after, str2)
    if result == None:
        return None
    return result.group(1)