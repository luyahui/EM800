#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 22:26:52 2017

@author: hanwang
"""

from bs4 import BeautifulSoup
import requests
import json
from datetime import date
import sys


def getArticleContent(url):
     
    article = ""
    
    web_data = requests.get(url)
    if web_data.status_code != 200:
        return
    
    soup = BeautifulSoup(web_data.text, "lxml")
    for p in soup.select("article h2, article p"):
        article += p.text
    
    return article


def getArticles(key_word):
    articles = []
    start = 1
    npp = 10
    flag = True
    while flag:
        page_url = 'http://searchapp.cnn.com/money-search/query.jsp?query={}&type=mixed&start={}&npp={}&s=all&primaryType=mixed&sortBy=date&csiID=csi4'.\
            format(key_word, start, npp)
        web_data = requests.get(page_url)
        if web_data.status_code != 200:
            break
        
        else:
            soup = BeautifulSoup(web_data.text, 'lxml')
            js_string = soup.select('#jsCode')[0].text
            parsed_json = json.loads(js_string)
            results = parsed_json['results'][0]

            for result in results:
                # we just need the articles in August 2017
                posted_date = date.fromtimestamp(float(result['mediaDateUts']))
                if posted_date > date(2017, 8, 31):
                    continue
                if posted_date < date(2017, 8, 1):
                    flag = False
                    break

                # this is not an article
                if result['metadata']['article']['author'] == '':
                    continue

                # retrieve the article's content
                article_url = result['url']
                article = {
                    'date': posted_date,
                    'title': result['title'],
                    'content': getArticleContent(article_url)
                }
                articles.append(article)

        start += npp
   
    return articles


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    key_word = 'apple'
    articles = getArticles(key_word)

    for article in articles:
        file_dir = 'CNNMoney/{}.txt'.format(article['date'].strftime('%Y%m%d'))
        with open(file_dir, 'a') as f:
            f.write(article['title'] + '\n')
            f.write(article['content'] + '\n')

    print len(articles)