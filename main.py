from pprint import pprint
from parsers import ProductParser

url = 'https://tap.az/elanlar/elektronika/oyunlar-ve-programlar/25372166'
parser = ProductParser(advert_url=url)
pprint(parser.parse())
