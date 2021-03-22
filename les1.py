import time
import json
from pathlib import Path
import requests


class Parse5ka:
    params = {
        "records_per_page": 20,
    }

    def __init__(self, start_url: str, result_path: Path):
        self.start_url = start_url
        self.result_path = result_path

    @staticmethod
    def _get_response(url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def run(self):
        for product in self._parse(self.start_url):
            self._save(product)

    def _parse(self, url):
        while url:
            response = self._get_response(url, params=self.params)
            data = response.json()
            url = data.get("next")
            for product in data.get("results", []):
                yield product

    def _save(self, data):
        file_path = self.result_path.joinpath(f'{data["id"]}.json')
        file_path.write_text(json.dumps(data, ensure_ascii=False))


class Parse5kaCategories(Parse5ka):

    def __init__(self, start_url: str, cat_url: str, result_path: Path):
        Parse5ka.__init__(self, start_url, result_path)
        self.cat_url = cat_url

    def run(self):
        for category in self._parse_cat(self.cat_url):
            self.params['categories'] = category.get('cat_code', [])
            for product in self._parse(self.start_url):
                category['products'].append(product)
            self._save(category)
        self.params.pop('categories')

    def _parse_cat(self, url):
        response = self._get_response(url)
        data = response.json()
        for category in data:
            cat_code = category.get('parent_group_code', [])
            cat_name = category.get('parent_group_name', [])
            cat_dict = {'cat_name': cat_name, 'cat_code': cat_code, 'products': []}
            yield cat_dict

    def _save(self, data):
        file_path = self.result_path.joinpath(f'{data["cat_code"]}.json')
        file_path.write_text(json.dumps(data, ensure_ascii=False))


if __name__ == '__main__':
    cat_file_path = Path(__file__).parent.joinpath('categories')
    if not cat_file_path.exists():
        cat_file_path.mkdir()
    category_url = 'https://5ka.ru/api/v2/categories/'
    products_url = 'https://5ka.ru/api/v2/special_offers/'
    parser = Parse5kaCategories(products_url, category_url, cat_file_path)
    parser.run()
