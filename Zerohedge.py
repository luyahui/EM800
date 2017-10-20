import requests
from bs4 import BeautifulSoup
import re
from datetime import date
import time
import sys


def getArticleContent(url):
    article = ""

    web_data = requests.get(url)
    if web_data.status_code != 200:
        return

    soup = BeautifulSoup(web_data.content, 'lxml')
    article = soup.select('main section section .content')[0].text
    return article


def getArticleComments(url):
    comments = []

    while url:
        web_data = requests.get(url)
        if web_data.status_code != 200:
            break

        soup = BeautifulSoup(web_data.content, 'lxml')

        for content in soup.select('.comment'):
            comment_time = time.strptime(
                content.select('.comment-header_date')[0].text,
                '%b %d, %Y %I:%M %p'
            )
            comment_date = date(comment_time.tm_year, comment_time.tm_mon, comment_time.tm_mday)
            comment_content = content.select('.comment-content')[0].text
            comment = {
                'date': comment_date,
                'content': comment_content
            }
            comments.append(comment)

        if len(soup.select('.pager-next')) == 0:
            url = None
        else:
            url = 'http://www.zerohedge.com' + soup.select('.pager-next a')[0]['href']

    return comments


def getArticles(key_word):
    articles = []

    page = 1
    flag = True
    while flag:
        page_url = 'http://www.zerohedge.com/search/apachesolr_search/{}?page={}&solrsort=created%20desc'\
            .format(key_word, page)
        web_data = requests.get(page_url)
        if web_data.status_code != 200:
            break

        soup = BeautifulSoup(web_data.content, 'lxml')

        dts = soup.select('.content dt')
        search_infos = soup.select('.content dd .search-info')
        for i in range(0, len(search_infos)):
            search_info = search_infos[i]
            posted_time = time.strptime(
                re.findall('\d{2}/\d{2}/\d{4}', search_info.text)[0],
                '%m/%d/%Y'
            )
            posted_date = date(posted_time.tm_year, posted_time.tm_mon, posted_time.tm_mday)

            if posted_date > date(2017, 8, 31):
                continue
            if posted_date < date(2017, 8, 1):
                flag = False
                break

            article_url = dts[i].select('a')[0]['href']

            article = {
                'date': posted_date,
                'title': dts[i].select('a')[0].text,
                'content': getArticleContent(article_url),
                'comments': getArticleComments(article_url)
            }

            articles.append(article)

        page += 1

    return articles


if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')

    articles = getArticles('apple')
    for article in articles:
        file_dir = 'Zerohedge/{}.txt'.format(article['date'].strftime('%Y%m%d'))
        with open(file_dir, 'a') as f:
            f.write(article['title'] + '\n')
            f.write(article['content'] + '\n')
        for comment in article['comments']:
            file_dir = 'Zerohedge/{}.txt'.format(comment['date'].strftime('%Y%m%d'))
            with open(file_dir, 'a') as f:
                f.write(comment['content'] + '\n')

    print len(articles)
