from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from avito_parse.spiders.avito import AvitoSpider


if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("avito_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(AvitoSpider)
    crawler_proc.start()
