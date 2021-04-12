from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hh_parse.spiders.hh_spider import HhSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("hh_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(HhSpider)
    crawler_proc.start()
