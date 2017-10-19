#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 20:26:59 2017

@author: hanwang
"""

from bs4 import BeautifulSoup
import requests
import sys
import time
from datetime import date
import json
import re

def getArticleContent(url):
     
    article = ""
    
    web_data = requests.get(url)
    if web_data.status_code != 200:
        return
    
    soup = BeautifulSoup(web_data.text, "lxml")
    for p in soup.select(".article-content > p"):
        article += p.text
    
    return article

def getArticles(stock_code):
    articles = []
    page_url = 'https://finance.google.com/finance/company_news?q=NASDAQ%3A' + stock_code + '&startdate=2017-08-01&enddate=2017-09-01'
    current_page = 0
    while page_url != None:
        web_data = requests.get(page_url)
        if web_data.status_code != 200:
            break
        else:
            soup = BeautifulSoup(web_data.text, 'lxml')
            if len(soup.select('.g-section.news.sfe-break-bottom-16')) == 0:
                break
            for news in soup.select('.g-section.news.sfe-break-bottom-16'):
                source = news.select('.byline > .src')[0].text
                if not source == "Motley Fool":
                    continue
                a = news.select('a')[0].text
                posted_date = news.select('.date')[0].text
                posted_time = time.strptime(posted_date, '%b %d, %Y')
                posted_date = date(posted_time.tm_year, posted_time.tm_mon, posted_time.tm_mday)
                href = news.select('a')[0]['href']
                if not href.startswith("http:"):
                    href = "http:" + href
                # print (a, time, href)
                article = {"title": a, "date": posted_date, "content": getArticleContent(href)}
                articles.append(article)    
                
            current_page += 10
            page_url = 'https://finance.google.com/finance/company_news?q=NASDAQ%3A' + stock_code + '&startdate=2017-08-01&enddate=2017-09-01&start=' + str(current_page) + '&num=10'
   
    return articles


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    stock_code = 'AAPL'
    articles = getArticles(stock_code)

    for article in articles:
        file_dir = 'MotleyFool/{}.txt'.format(article['date'].strftime('%Y%m%d'))
        with open(file_dir, 'a') as f:
            f.write(article['title'] + '\n')
            f.write(article['content'] + '\n')

    print(len(articles))

