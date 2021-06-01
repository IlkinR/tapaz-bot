import re
import os.path
import datetime

import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse

from collections import namedtuple

Product = namedtuple('Product', ['id', 'date'])


class StopGame:
    # host = 'https://tap.az'
    host = 'https://tap.az/elanlar/elektronika/komputer-avadanliqi/'
    # url = 'https://tap.az/elanlar/elektronika/komputer-avadanliqi?p%5B834%5D=7400&q%5Bprice%5D%5B%5D=40&q%5Bprice%5D%5B%5D=100'
    url = 'https://tap.az/elanlar/elektronika/komputer-avadanliqi?q%5Bprice%5D%5B%5D=100&q%5Bprice%5D%5B%5D=2000'
    lastkey = ""
    lastkey_file = ""

    def __init__(self, lastkey_file):
        self.lastkey_file = lastkey_file

        # If file exists, read the date of last written product
        if (os.path.exists(lastkey_file)):
            self.lastkey = open(lastkey_file, 'r').read()
            print('Zdes yest lastkey {}'.format(self.lastkey))
        else:  # Else write to the file the date of last product
            f = open(lastkey_file, 'w')
            self.lastkey = self.get_lastkey()
            f.write(self.lastkey)
            f.close()

    def new_games(self):
        r = requests.get(self.url)
        html = BS(r.content, 'html.parser')

        new = []
        # items = html.select('.categories-products > .js-endless-container > .products-i > a')
        timestamps = self.datetimestamp(html)
        for timestamp in timestamps:
            # dt = timestamp.strptime("%Y-%m-%d %H:%M:%S")
            key_date = datetime.datetime.strptime(self.lastkey, "%Y-%m-%d %H:%M:%S")
            # key = self.parse_href(i['href'])
            if key_date < timestamp:
                new.append(timestamp)
        return new  # returns list of new product's datetimestamps

    def game_info(self, uri):
        link = self.host + uri
        r = requests.get(link)
        html = BS(r.content, 'html.parser')

        # parse poster image url
        # poster = re.match(r'background-image:\s*url\((.+?)\)', html.select('.image-game-logo > .image')[0]['style'])
        # poster = [j.get('href') for j in i.find_all('a') for i in html.find_all('div', {'class': 'photos'})][0]
        posters = []
        for i in html.find_all('div', {'class': 'photos'}):
            for j in i.find_all('a'):
                posters.append(j.get('href'))

        print('Proverka salam aleykum')
        # remove some stuff
        # remels = html.select('.article.article-show > *')
        # for remel in remels:
        #   remel.extract()
        property_names = []
        property_values = []
        for i in html.select('.properties > .property > .property-name'):
            property_names.append(i.text)
        for j in html.select('.properties > .property > .property-value'):
            property_values.append(j.text)
        properties = {property_names[i]: property_values[i] for i in range(len(property_names))}

        # form data
        info = {
            # product_date = ...
            "id": self.parse_href(uri),
            "title": html.select('.title-container > h1')[0].text,
            "link": link,
            "image": posters[0],
            "price": html.select('.price')[0].text,
            "phone": html.select('.phone')[0].text,
            "description": html.select('.lot-text > p')[0].text
            # "score": self.identify_score(html.select('.game-stopgame-score > .score')[0]['class'][1]),
        }

        info.update(properties)

        return info

    def download_image(self, url):
        r = requests.get(url, allow_redirects=True)

        a = urlparse(url)
        filename = os.path.basename(a.path)
        open(filename, 'wb').write(r.content)

        return filename

    # def identify_score(self, score):
    #   if(score == 'score-1'):
    #     return "Мусор 👎"
    #   elif(score == 'score-2'):
    #     return "Проходняк ✋"
    #   elif(score == 'score-3'):
    #     return "Похвально 👍"
    #   elif(score == 'score-4'):
    #     return "Изумительно 👌"

    def datetimestamp(self, html):
        dates = []
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        timestamps = html.select(
            '.categories-products > .js-endless-container > .products-i > .products-link > .products-created')
        for timestamp in timestamps:
            if 'dünən' not in str(timestamp.text) and 'bugün' not in str(timestamp.text):
                #             print(timestamp.text)
                continue
            if 'bugün' in timestamp.text:
                dates.append(datetime.datetime.combine(today, datetime.datetime.strptime(timestamp.text.split()[-1],
                                                                                         '%H:%M').time()))
            elif 'dünən' in timestamp.text:
                dates.append(datetime.datetime.combine(yesterday, datetime.datetime.strptime(timestamp.text.split()[-1],
                                                                                             '%H:%M').time()))
        return dates  # returns list of today's and yesterday's dates in default format

    def get_lastkey(self):
        r = requests.get(self.url)
        html = BS(r.content, 'html.parser')

        # items = html.select('.categories-products > .js-endless-container > .products-i > a')
        # timestamps = html.select(
        #     '.categories-products > .js-endless-container > .products-i > .products-link > .products-created')
        print('A eto mi was polucim, no vradle {}'.format(self.datetimestamp(html)[0].strftime("%Y-%m-%d %H:%M:%S")))
        return self.datetimestamp(html)[0].strftime("%Y-%m-%d %H:%M:%S")  # returns date of last product

    def parse_href(self, href):
        pass

    # result = re.match(r'\/elanlar/elektronika/komputer-avadanliqi\/(\d+)', href)
    # return result.group(1)

    def update_lastkey(self, new_key):
        self.lastkey = new_key
        print('Delayem update last keya - {}'.format(self.lastkey))
        with open(self.lastkey_file, "r+") as f:
            data = f.read()
            f.seek(0)
            f.write(str(new_key))
            f.truncate()

        return new_key
