"""
Название объявления
Список фото объявления (ссылки)
Список характеристик
Описание объявления
ссылка на автора объявления
дополнительно попробуйте вытащить телефона
"""

import scrapy
import re
import pymongo
from urllib.parse import unquote


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            url = a.attrib.get("href")
            yield response.follow(url, callback=callback, **kwargs)

    @staticmethod
    def get_data_from_script(res, pattern, decode=False):
        marker = "window.transitState = decodeURIComponent"
        for script in res.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    text = (unquote(script.css("::text").extract_first().encode('utf-8').decode('utf-8'))
                            if decode
                            else script.css("::text").extract_first())
                    result = re.findall(pattern, text)
                    return result if result else None
            except TypeError:
                pass

    def parse(self, response):
        yield from self._get_follow(
            response, "div.TransportMainFilters_brandsList__2tIkv a.blackLink", self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, "div.Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
            self.car_parse,
        )

    def car_parse(self, response):
        specs = response.css("div.AdvertCard_specs__2FEHc div.AdvertSpecs_row__ljPcX ::text").extract()
        author_pattern = re.compile(r'youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar')
        photos_pattern = re.compile(r'big","(.*?)","medium')
        try:
            data = {
                "url": response.url,
                "title": response.css("div.AdvertCard_advertTitle__1S1Ak::text").extract_first(),
                "price": float(
                    response.css("div.AdvertCard_price__3dDCr::text")
                    .extract_first()
                    .replace("\u2009", "")
                ),
                "photos_list": self.get_data_from_script(response, photos_pattern, True),
                "specs": {a: b for a, b in list(zip(specs[::2], specs[1::2]))},
                "description":
                    response.css(
                        'div.AdvertCard_description__2bVlR div.AdvertCard_descriptionInner__KnuRi::text'
                    ).extract_first(),
                "author_url": response.urljoin(f"/user/{self.get_data_from_script(response, author_pattern)[0]}").
                    replace("auto.", "", 1)
            }
            self.db_client["gb_parse_auto_youla"][self.name].insert_one(data)
        except(AttributeError, ValueError):
            pass
