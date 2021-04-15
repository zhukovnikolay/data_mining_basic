from urllib.parse import urljoin

from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose


def clear_price(price: str) -> float:
    try:
        result = float(price.replace("\u2009", ""))
    except ValueError:
        result = None
    return result


def get_params(item: str) -> dict:
    selector = Selector(text=item)
    not_null_selector = [i for i in selector.xpath("//text()").extract() if i != ' ']
    data = {
        "name": not_null_selector[0].strip(),
        "value": not_null_selector[1].strip().replace('\xa0', ' ')
    }
    return data


def avito_user_url(user_url):
    return urljoin('https://www.avito.ru', user_url.split('&')[0])


def clear_title(title):
    return title.replace('\xa0', '')


def clear_address(address):
    return address.replace('\n', '').strip()


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = MapCompose(clear_title)
    title_out = TakeFirst()
    address_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    params_in = MapCompose(get_params)
    author_url_in = MapCompose(avito_user_url)
    author_url_out = TakeFirst()
