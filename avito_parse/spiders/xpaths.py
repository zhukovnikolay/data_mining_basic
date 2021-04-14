AVITO_PAGE_XPATH = {
    "pagination": '//div[@class="index-content-2lnSO"]//'
                  'div[contains(@data-marker, "pagination-button")]/'
                  'span[@class="pagination-item-1WyVp"]/@data-marker',
    "advert": '//div[@data-marker="item"]//a[@data-marker="item-title"]/@href'
}

AVITO_OBJECT_XPATH = {
    'title': '//h1[@class="title-info-title"]/span[@itemprop="name"]/text()',

    'price': '//div[contains(@class, "price-value-prices-wrapper")]'
              '/ul[contains(@class, "price-value-prices-list")]'
              '/li[contains(@class, "price-value-prices-list-item_pos-first")]'
              '/text()',

    'address': '//div[@itemprop="address"]/span/text()',

#!    'params': '//div[@class="item-params"]/ul[@class="item-params-list"]/li[@class="item-params-list-item"]',

    'author_url': '//div[@data-marker="seller-info/name"]/a/@href'
}
