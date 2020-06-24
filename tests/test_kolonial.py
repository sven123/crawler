from unittest import TestCase
from unittest.mock import Mock
import vcr
import requests
from crawler.kolonial import KolonialHandlers, Product
from crawler.crawler import NO_HANDLER


class KolonialHandlersTest(TestCase):
    def setUp(self):
        self.mock_emitter = Mock()
        self.handlers = KolonialHandlers("https://kolonial.no", self.mock_emitter)

    def test_kolonial_url(self):
        self.assertEqual(self.handlers.url, "https://kolonial.no")

    def test_should_crawl(self):
        samples = [
            ("/kategorier/283-fisk-og-sjomat/", True),
            ("/produkter/9428-crispisalat-beger-norge/", False),
            ("/introduksjon/", False),
            ("/", True),
            ("/produkter/", False),
        ]

        for url, expected in samples:
            result = self.handlers.should_crawl(url)
            self.assertEqual(result, expected)

    def test_handler(self):
        samples = [
            ("/kategorier/283-fisk-og-sjomat/", NO_HANDLER),
            (
                "/produkter/9428-crispisalat-beger-norge/",
                self.handlers.product_handler,
            ),
            ("/introduksjon/", NO_HANDLER),
            ("/", NO_HANDLER),
            ("/produkter/", NO_HANDLER),
        ]

        for url, expected in samples:
            result = self.handlers.handler(url)
            self.assertEqual(result, expected)

    @vcr.use_cassette("fixtures/vcr_cassettes/product_handler.yml")
    def test_product_handler(self):
        url = f"{self.handlers.url}/produkter/9329-store-bananer-colombia-guatemala/"

        response = requests.get(url)
        self.handlers.product_handler(response.text)

        self.mock_emitter.emit.assert_called_once_with(
            Product(title="Store Bananer Colombia/ Guatemala, 1 stk", price=5.80),
        )
