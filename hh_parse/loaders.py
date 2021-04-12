from urllib.parse import urljoin

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose


def flat_text(items):
    return "\n".join(items)


def split_list(scope_list):
    return scope_list.split(',')


def hh_user_url(user_id):
    return urljoin("https://hh.ru/", user_id)


class HHLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = flat_text
    description_out = flat_text
    author_in = MapCompose(hh_user_url)
    author_out = TakeFirst()


class HHCompanyLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    description_out = flat_text
    scope_list_out = split_list
