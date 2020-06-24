import asyncio
from aiounittest import AsyncTestCase as TestCase
from unittest.mock import Mock, AsyncMock, patch
import vcr
from crawler.crawler import Crawler, NO_HANDLER

import requests


class CrawlertTest(TestCase):
    def setUp(self):
        self.mock_handler = Mock()
        self.mock_http = AsyncMock()
        self.crawler = Crawler(self.mock_http, self.mock_handler)

    @vcr.use_cassette("fixtures/vcr_cassettes/links.yml")
    def test_scrape_links(self):
        url = "https://kolonial.no"
        response = requests.get(f"{url}/produkter/")

        links = self.crawler.scrape_links(response.text)
        self.assertEqual(links[-1], "/personvern/")

    @patch.object(Crawler, "scrape_links")
    async def test_crawl(self, mock_scrape_links):
        self.mock_handler.should_crawl.return_value = True
        sample = "/"
        result = await self.crawler.crawl(sample)
        self.mock_http.get.assert_called_with(f"{self.mock_handler.url}{sample}")
        self.assertTrue(sample in self.crawler.already_crawled)
        self.assertEqual(result, mock_scrape_links())

    async def test_crawl_should_not_crawl(self):
        self.mock_handler.should_crawl.return_value = False
        self.mock_handler.handler.return_value = NO_HANDLER
        sample = "/static/image"
        result = await self.crawler.crawl(sample)
        self.mock_http.get.assert_not_called()
        self.assertTrue(sample in self.crawler.already_crawled)
        self.assertEqual(result, [])

    async def test_crawl_already_crawled(self):
        self.crawler.already_crawled.add("/")
        result = await self.crawler.crawl("/")
        self.mock_http.get.assert_not_called()
        self.assertEqual(result, [])

    async def test_crawl_with_handler(self):
        mock_handler = Mock()
        self.mock_handler.should_crawl.return_value = False
        self.mock_handler.handler.return_value = mock_handler

        sample = "/produkter/1234-foo-bar/"
        result = await self.crawler.crawl(sample)

        self.mock_handler.handler.assert_called_once_with(sample)
        self.mock_http.get.assert_called_with(f"{self.mock_handler.url}{sample}")
        mock_handler.assert_called_once_with(self.mock_http.get.return_value.text)
        self.assertTrue(sample in self.crawler.already_crawled)
        self.assertEqual(result, [])
