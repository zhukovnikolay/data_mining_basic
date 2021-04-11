"""
Задача: Обойти с точки входа все вакансии и собрать след данные:
1. название вакансии
2. оклад (строкой от до или просто сумма)
3. Описание вакансии
4. ключевые навыки - в виде списка названий
5. ссылка на автора вакансии

Перейти на страницу автора вакансии,
собрать данные:
1. Название
2. сайт ссылка (если есть)
3. сферы деятельности (списком)
4. Описание

Обойти и собрать все вакансии данного автора.
"""

import scrapy
from urllib.parse import urljoin
from hh_parse.loaders import HHLoader


class HhSpider(scrapy.Spider):
    name = 'hh_spider'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    hh_pagination_xpath = {
        "pagination": '//div[@data-qa="pager-block"]//a[@data-qa="pager-next"]/@href',
        "vacancy": '//div[contains(@data-qa, "vacancy-serp__vacancy")]//'
                   'a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }

    hh_vacancy_xpath = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]/span/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//'
                  'div[contains(@data-qa, "skills-element")]/'
                  'span[@data-qa="bloko-tag__text"]/text()',
        "author": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    hh_company_xpath = {
        "title": '//h1[@data-qa="bloko-header-1"]/span[@data-qa="company-header-title-name"]/text()',
        "url": '//p[@class="vacancy-salary"]/span/text()',
        "scope_list": '//div[@data-qa="vacancy-description"]//text()',
        "description": '//div[@class="bloko-tag-list"]//'
                  'div[contains(@data-qa, "skills-element")]/'
                  'span[@data-qa="bloko-tag__text"]/text()'
    }

    def _get_follow_xpath(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response):
        callbacks = {"pagination": self.parse, "vacancy": self.vacancy_parse}

        for key, xpath in self.hh_pagination_xpath.items():
            yield from self._get_follow_xpath(response, xpath, callbacks[key])

    def vacancy_parse(self, response):
        yield from self._get_follow_xpath(
            response, urljoin("https://hh.ru/", response.xpath(self.hh_vacancy_xpath['author'])), self.company_parse,
        )
        loader = HHLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self.hh_vacancy_xpath.items():
            loader.add_xpath(key, xpath)

        yield loader.load_item()

    def company_parse(self, response):
        pass
