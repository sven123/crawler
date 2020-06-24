import re
import asyncio


NO_HANDLER = object()


class Crawler:
    HREF_PATTERN = re.compile(r'href="(/.*?)"')

    def __init__(self, http_client, link_handlers):
        self.link_handlers = link_handlers
        self.http_client = http_client
        self.already_crawled = set()
        self.already_crawled_lock = asyncio.Lock()

    def scrape_links(self, text):
        return self.HREF_PATTERN.findall(text)

    async def crawl(self, link):

        async with self.already_crawled_lock:
            if link in self.already_crawled:
                return []

            self.already_crawled.add(link)

        if self.link_handlers.should_crawl(link):
            response = await self.http_client.get(f"{self.link_handlers.url}{link}")
            return self.scrape_links(response.text)
        else:
            handler = self.link_handlers.handler(link)
            if handler is NO_HANDLER:
                return []

            response = await self.http_client.get(f"{self.link_handlers.url}{link}")
            handler(response.text)
            return []
