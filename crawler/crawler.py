import re
from requests import get

NO_HANDLER = object()
HREF_PATTERN = re.compile(r'href="(/.*?)"')


def scrape_links(text):
    return HREF_PATTERN.findall(text)


class Crawler:
    def __init__(self, http_client, link_handlers):
        self.link_handlers = link_handlers
        self.http_client = http_client
        self.already_crawled = set()

    def crawl(self, link):
        if link in self.already_crawled:
            return []

        self.already_crawled.add(link)

        if self.link_handlers.should_crawl(link):
            response = self.http_client.get(f"{self.link_handlers.url}{link}")
            return scrape_links(response.text)
        else:
            handler = self.link_handlers.handler(link)
            if handler is NO_HANDLER:
                return []

            response = self.http_client.get(f"{self.link_handlers.url}{link}")
            handler(response.text)
            return []
