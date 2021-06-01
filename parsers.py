from typing import Dict, Tuple

from utils import get_soup


class ProductParser:
    # TODO: Add doc strings to methods and class
    # TODO: Add defensive programming into methods

    def __init__(self, advert_url: str) -> None:
        self.advert_url = advert_url
        self.soup = get_soup(self.advert_url)

    def _get_properties(self) -> Dict[str, str]:
        prop_names = {tag.text for tag in self.soup.select('td.property-name')}
        prop_value = {tag.text for tag in self.soup.select('td.property-value')}
        return dict(zip(prop_names, prop_value))

    def _get_price(self) -> int:
        price_tag = self.soup.find('span', class_='price-val')
        return int(price_tag.text)

    def _get_phone(self) -> str:
        phone_tag = self.soup.find('a', class_='shop-phones--number')
        return phone_tag.text

    def _get_location(self) -> Tuple[str, str]:
        location_tag = self.soup.find('a', class_='shop--location')
        url, name = location_tag.get('href'), location_tag.text
        return url, name

    def _get_data(self) -> Dict[str, str]:
        data_tags = self.soup.select('div.lot-info > p')
        data_tags = [tag.text.split(':') for tag in data_tags]
        data_names = [tag[0] for tag in data_tags]
        data_values = [tag[1] for tag in data_tags]
        return dict(zip(data_names, data_values))
