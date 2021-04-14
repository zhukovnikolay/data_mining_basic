"""
Источник https://www.avito.ru/krasnodar/kvartiry/prodam
задача обойти пагинацию и подразделы квартир в продаже.
Собрать данные:
URL
Title
Цена
Адрес (если доступен)
Параметры квартиры (блок под фото)
Ссылку на автора
Дополнительно но не обязательно вытащить телефон автора
"""
import scrapy
from avito_parse.loaders import AvitoLoader
from avito_parse.spiders.xpaths import AVITO_PAGE_XPATH, AVITO_OBJECT_XPATH


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']
    current_page = 1

    def _get_follow_advert_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response):
        callbacks = {"pagination": self.parse, "advert": self.advert_parse}
        if self.current_page == 1:
            max_page = int(response.xpath(AVITO_PAGE_XPATH['pagination']).extract()[-1].
                           split('(')[-1].replace(')', ''))
        for key, xpath in AVITO_PAGE_XPATH.items():
            if key == 'pagination' and self.current_page <= max_page:
                self.current_page += 1
                yield response.follow(
                    f'?p={self.current_page}',
                    callback=callbacks[key]
                )
            elif key == 'advert':
                yield from self._get_follow_advert_xpath(response, xpath, callbacks[key])

    def advert_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in AVITO_OBJECT_XPATH.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()
