import re


NO_HANDLER = object()


class Crawler:
    HREF_PATTERN = re.compile(r'href="(/.*?)"')

    def __init__(self, robots_agent, http_client, link_handlers):
        self.link_handlers = link_handlers
        self.http_client = http_client
        self.already_crawled = set()
        self.robots_agent = robots_agent

    def scrape_links(self, text):
        return self.HREF_PATTERN.findall(text)

    async def crawl(self, link):
        if link in self.already_crawled:
            return []

        self.already_crawled.add(link)
        if not self.robots_agent.allowed(link):
            return []

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
