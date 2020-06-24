import re
from collections import namedtuple
from crawler import crawler


Product = namedtuple("Product", ["title", "price"])


class KolonialHandlers:
    CATEGORY_PATTERN = re.compile(r"^/kategorier/\d+")
    PRODUCT_PATTERN = re.compile(r"^/produkter/\d+")
    TITLE_PATTERN = re.compile(r'<meta property="og:title" content="(.*?)">')
    PRICE_PATTERN = re.compile(
        r'<meta property="product:price:amount" content="(.*?)">'
    )

    def __init__(self, url, emitter):
        self.url = url
        self.emitter = emitter

    def should_crawl(self, link):
        if self.CATEGORY_PATTERN.match(link) or link == "/":
            return True
        return False

    def handler(self, link):
        if self.PRODUCT_PATTERN.match(link):
            return self.product_handler
        return crawler.NO_HANDLER

    def product_handler(self, text):
        title = self.TITLE_PATTERN.search(text)[1]
        price = float(self.PRICE_PATTERN.search(text)[1])
        self.emitter.emit(Product(title=title, price=price))
