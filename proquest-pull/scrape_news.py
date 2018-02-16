from bs4 import BeautifulSoup
from selenium import webdriver

import re
import csv

browser = webdriver.Chrome('./chromedriver.exe')
def get_articles(url, filename):
    with open(filename, "w+") as outfile:
        j = 1
        browser.get(url)
        while True:
            if j > 20: break
            # try:
            split = re.split("/[0-9]*\?", browser.current_url)
            browser.get(split[0] + "/" + str(j) + "?" + split[1])
            soup = BeautifulSoup(browser.page_source, "html.parser")
            body = soup.find("body")
            wrapper = body.find("div", id="wrapper")
            container = wrapper.find("div", class_="container")
            start = container.find("div", id="start")
            mainContent = start.find("div", id="mainContentRight")
            resultContainer = mainContent.find("div", class_="resultListContainer ltr")
            resultItems = resultContainer.find("ul")
            results = resultItems.find_all("li", class_="resultItem ltr")
            i = 1
            for result in results:
                item = result.find("div", id=re.compile("mlditem"))
                contentarea = item.find("div", class_="contentArea")
                mldcopy = contentarea.find("div", id=re.compile("mld"))
                h3 = mldcopy.find("h3")
                a = h3.find("a")
                # print("search.proquest.com" + a['href'])
                outfile.writelines(a['href'] + "\n")
            j += 1
get_articles("https://search.proquest.com/search/1344155?accountid=12492", "vernacular_articles.txt")
get_articles("https://search.proquest.com/search/1346455?accountid=12492", "scientific_articles.txt")
