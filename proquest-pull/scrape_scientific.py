# http://search.proquest.com/globalnews/results/ADA0AE158954F81PQ/1?accountid=14026
import csv
import re
import wget
from selenium import webdriver
import os.path

def do_pass(corpus_type):
    browser = webdriver.Chrome('./chromedriver.exe')
    visited = []
    mode = "r" if os.path.isfile(corpus_type + "_successes.txt") else "w+"
    with open(corpus_type + "_successes.txt", mode) as file:
        for line in file:
            visited.append(line)
    with open(corpus_type + "_failures.txt", mode) as file:
        for line in file:
            visited.append(line)

    with open(corpus_type + "_articles.txt", "r") as infile:
        with open(corpus_type + ".csv", "a+") as csvout:
            fieldnames = ['title', 'text']
            writer = csv.DictWriter(csvout, fieldnames=fieldnames)
            writer.writeheader()
            with open(corpus_type + "_successes.txt", "a+") as outfile:
                for line in infile:
                    split = re.split("/[0-9]*\?", line)
                    url = split[0].rsplit("/", 1)[0]
                    label = url.rsplit("/", 1)[1]
                    if line in visited:
                        continue
                    try:
                        browser.get(url)
                        link = browser.find_element_by_id("downloadPDFLink").get_attribute('href')
                        print(link)
                        if not os.path.exists("./scientific"):
                            os.makedirs("./scientific")
                        wget.download(link, './scientific/' + label + '.pdf')
                        outfile.writelines(line)
                    except:
                        print(url)
                        browser.close()
                        return line
    browser.close()

def run_passes(corpus_type):
    old = ""
    prev = ""
    while True:
        resp = do_pass(corpus_type)
        if resp == "done":
            break
        if resp == old:
            if prev == resp:
                with open(corpus_type + "_failures.txt", "a+") as file:
                    file.writelines(resp)
            prev = old
        old = resp

run_passes("scientific") 