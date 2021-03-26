"""
Источник https://magnit.ru/promo/?geo=moskva

Необходимо собрать структуры товаров по акции и сохранить их в MongoDB
пример структуры и типы обязательно хранить поля даты как объекты datetime
{
    "url": str,
    "promo_name": str,
    "product_name": str,
    "old_price": float,
    "new_price": float,
    "image_url": str,
    "date_from": "DATETIME",
    "date_to": "DATETIME",
}
"""

import time
import datetime
import requests
from urllib.parse import urljoin
import bs4
import pymongo


class MagnitParse:
    def __init__(self, start_url, db_url):
        self.start_url = start_url
        client = pymongo.MongoClient(db_url)
        self.db = client["magnit_db"]

    @staticmethod
    def get_response(start_url, *args, **kwargs):
        for _ in range(15):
            response = requests.get(start_url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)
        raise ValueError("URL DIE")

    def get_soup(self, start_url, *args, **kwargs) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self.get_response(start_url, *args, **kwargs).text, "lxml")
        return soup

    @staticmethod
    def datetime_transform(datetime_list):
        dt_dict = {
            'января': '01',
            'февраля': '02',
            'марта': '03',
            'апреля': '04',
            'мая': '05',
            'июня': '06',
            'июля': '07',
            'августа': '08',
            'сентября': '09',
            'октября': '10',
            'ноября': '11',
            'декабря': '12'
        }
        dt_list = []
        for dt in datetime_list:
            dt = str(dt).replace('</p>', '')
            dt_string = f'{dt.split()[-2]} ' \
                        f'{dt.split()[-1].replace(dt.split()[-1], dt_dict[dt.split()[-1]])} ' \
                        f'{datetime.date.today().year}'
            dt_list.append(datetime.datetime.strptime(dt_string, '%d %m %Y'))
        # на случай, если акция только один день (значения date_from и date_to будут одинаковы)
        if len(dt_list) == 1:
            dt_list.append(dt_list[0])
        return dt_list

    @property
    def template(self):
        data_template = {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href", "/")),
            "promo_name": lambda a: a.find("div", attrs={"class": "card-sale__name"}).text,
            "product_name": lambda a: a.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda a: float(
                a.find("div", attrs={"class": "label__price_old"}).
                find("span", attrs={"class": "label__price-integer"}).text +
                '.' +
                a.find("div", attrs={"class": "label__price_old"}).
                find("span", attrs={"class": "label__price-decimal"}).text),
            "new_price": lambda a: float(
                a.find("div", attrs={"class": "label__price_new"}).
                find("span", attrs={"class": "label__price-integer"}).text +
                '.' +
                a.find("div", attrs={"class": "label__price_new"}).
                find("span", attrs={"class": "label__price-decimal"}).text),
            "image_url": lambda a: urljoin(
                self.start_url, a.find("picture").find("img").attrs.get("data-src", "/")),
            "date_from": lambda a: self.datetime_transform(a.find("div", attrs={"class": "card-sale__date"}).
                                                           find_all("p"))[0],
            "date_to": lambda a: self.datetime_transform(a.find("div", attrs={"class": "card-sale__date"}).
                                                         find_all("p"))[1],
        }
        return data_template

    def run(self):
        self.db["Magnit"].drop()
        for product in self._parse(self.get_soup(self.start_url)):
            self.save(product)

    def _parse(self, soup):
        products_a = soup.find_all("a", attrs={"class": "card-sale"})
        for prod_tag in products_a:
            product_data = {}
            for key, func in self.template.items():
                try:
                    product_data[key] = func(prod_tag)
                except AttributeError:
                    pass
            yield product_data

    def save(self, data):
        collection = self.db["Magnit"]
        collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    mongo_url = "mongodb://localhost:27017"
    parser = MagnitParse(url, mongo_url)
    parser.run()
