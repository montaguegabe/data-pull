# source: https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py

import requests

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