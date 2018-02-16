# http://search.proquest.com/globalnews/results/ADA0AE158954F81PQ/1?accountid=14026
import requests
import csv
import re
from bs4 import BeautifulSoup
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
                    if line in visited:
                        continue
                    try:
                        browser.get(url)
                        # r = requests.get("http://" + url)
                        # soup = BeautifulSoup(r.content, "html.parser")
                        soup = BeautifulSoup(browser.page_source, "html.parser")
                        body = soup.find("body")
                        wrapper = body.find("div", id="wrapper")
                        content = wrapper.find("div", id="content")
                        start = content.find("div", id="start")
                        columnsWrapper = start.find("div", id="columnsWrapper")
                        mainContent = columnsWrapper.find("div", id="mainContentLeft")
                        article = mainContent.find("article")
                        contentHeader = article.find("div")
                        textWrapper = contentHeader.find("div")
                        parent = textWrapper.find("div", class_="col-sm-7 col-md-9 col-lg-10")
                        title = parent.find("h1").text

                        tabpanel = article.find("div", class_="tabs docview")
                        tabcontent = tabpanel.find("div", class_="tab-content")
                        fulltex_null = tabcontent.find("div")
                        padingDocview = fulltex_null.find("div", class_="contentPadingDocview")
                        readableContent = padingDocview.find("div", id="readableContent")
                        div = readableContent.find("div")
                        div2 = div.find("div")
                        zoneId = div2.find("div", id="fullTextZoneId")
                        text = zoneId.find("text")
                        out_string = ""
                        paragraphs = text.find_all("p")
                        for paragraph in paragraphs:
                            out_string += paragraph.text + "\n"
                        writer.writerow({'title': title.encode('utf-8'), 'text': out_string.encode('utf-8')})
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

# run_passes("scientific") Need to resolve pdf text issue...
run_passes("vernacular")