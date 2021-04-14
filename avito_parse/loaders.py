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
    data = {
        "name": selector.xpath("//span/text()").extract_first(),
        "value": selector.xpath("//text()").extract_first(),
    }
    return data

def avito_user_url(user_url):
    return user_url.split('&')[0]

# title = replace('\xa0','')
class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    address_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    params_in = MapCompose(get_params)
    author_url_in = MapCompose(avito_user_url)
    author_url_out = TakeFirst()
