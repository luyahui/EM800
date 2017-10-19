import CNNMoney
import MotleyFool
import sys

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    key_word = 'apple'

    articles = CNNMoney.getArticles(key_word)
    articles += MotleyFool.getArticles(key_word)

    for article in articles:
        file_dir = 'News/{}.txt'.format(article['date'].strftime('%Y%m%d'))
        with open(file_dir, 'a') as f:
            f.write(article['title'] + '\n')
            f.write(article['content'] + '\n')