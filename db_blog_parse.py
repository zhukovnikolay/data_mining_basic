import typing
import requests
import bs4
import datetime
import time
from urllib.parse import urljoin
from database import db, models


class GbBlogParse:
    def __init__(self, start_url, database: db.Database, comments_url):
        self.db = database
        self.start_url = start_url
        self.done_urls = set()
        self.tasks = []
        self.comments_url = comments_url
        self.params = {
            "commentable_type": "Post",
            "order": "desc"
        }

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def _get_response(self, url, *args, **kwargs) -> requests.Response:
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)

    def _get_soup(self, url, *args, **kwargs) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")
        return soup

    def parse_comments(self, soup):
        self.params["commentable_id"] = \
            soup.find("div", attrs={"class": "referrals-social-buttons-small-wrapper"}).attrs.get("data-minifiable-id")
        response = self._get_response(self.comments_url, params=self.params)
        data = response.json()
        comments_list = []
        session = self.db.maker()
        while data:
            comment = data.pop(-1)
            writer_url = comment.get("comment").get("user").get("url")
            writer_name = comment.get("comment").get("user").get("full_name")
            comment_data = {
                "comment_data": {
                    "id": comment.get("comment").get("id"),
                    "comment_text": comment.get("comment").get("body"),
                    "parent_id": comment.get("comment").get("parent_id")
                },
                "writer_data": {
                    "url": writer_url,
                    "name": writer_name
                }
            }
            comments_list.append(comment_data)
            if len(comment.get("comment").get("children")) != 0:
                data.extend(comment.get("comment").get("children"))
        session.close()
        return comments_list

    def parse_post(self, url, soup):
        author_tag = soup.find("div", attrs={"itemprop": "author"})
        data = {
            "post_data": {
                "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                "post_datetime": datetime.datetime.strptime(soup.find("time").attrs.get("datetime"),
                                                            "%Y-%m-%dT%H:%M:%S%z"),
                "post_image_url": soup.find("img").attrs.get("src"),
                "url": url,
            },
            "author_data": {
                "url": urljoin(url, author_tag.parent.attrs.get("href")),
                "name": author_tag.text,
            },
            "tags_data": [
                {"url": urljoin(url, tag_a.attrs.get("href")), "name": tag_a.text}
                for tag_a in soup.find_all("a", attrs={"class": "small"})
            ],
            "comments_data": self.parse_comments(soup)
        }
        return data

    def parse_feed(self, url, soup):
        ul = soup.find("ul", attrs={"class": "gb__pagination"})
        pag_urls = set(
            urljoin(url, url_a.attrs.get("href"))
            for url_a in ul.find_all("a")
            if url_a.attrs.get("href")
        )
        for pag_url in pag_urls:
            if pag_url not in self.done_urls:
                task = self.get_task(pag_url, self.parse_feed)
                self.done_urls.add(pag_url)
                self.tasks.append(task)

        post_urls = set(
            urljoin(url, url_a.attrs.get("href"))
            for url_a in soup.find_all("a", attrs={"class": "post-item__title"})
            if url_a.attrs.get("href")
        )
        for post_url in post_urls:
            if post_url not in self.done_urls:
                task = self.get_task(post_url, self.parse_post)
                self.done_urls.add(post_url)
                self.tasks.append(task)

    def run(self):
        task = self.get_task(self.start_url, self.parse_feed)
        self.tasks.append(task)
        self.done_urls.add(self.start_url)

        for task in self.tasks:
            task_result = task()
            if task_result:
                self.save(task_result)

    def save(self, data):
        self.db.create_post(data)


if __name__ == "__main__":
    comments_url = "https://geekbrains.ru/api/v2/comments"
    database = db.Database("sqlite:///db_blog.db")
    parser = GbBlogParse("https://gb.ru/posts", database, comments_url)
    parser.run()
