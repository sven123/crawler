"""
Scrape kolonial.no

usage:
    scrape [--concurrent=N] [--site=URL] [--minimum-wait=S] [--maximum-wait=S] [--max-items=N]

options:
    --concurrent=N, -c        number of concurrent requests [default: 1]
    --site=SITE, -s           url for site to scrape [default: https://kolonial.no]
    --minimum-wait=S, -i      minum wait time between requests [default: 1.0]
    --maximum-wait=S, -a      max seconds to wait before next request [default: 2.0]
    --max-items=N, -n         max number of items to fetch [default: 100]
"""


from docopt import docopt
from collections import namedtuple
import random
import time
import asyncio
from reppy.robots import Robots
import aiohttp
from crawler.crawler import Crawler
from crawler.kolonial import KolonialHandlers


USER_AGENT = "testcrawler / 0.1 an execercise"
Response = namedtuple("Response", ["status_code", "text"])


def main():
    args = docopt(__doc__)

    concurrent = int(args["--concurrent"])
    site = args["--site"]
    minimum_wait = float(args["--minimum-wait"])
    maximum_wait = float(args["--maximum-wait"])
    max_items = int(args["--max-items"])

    asyncio.run(_main(
        site, concurrent, minimum_wait, maximum_wait, max_items))


async def _main(site, concurrent, minimum_wait, maximum_wait, max_items):
    start_time = time.time()

    robot_agent = create_robot_agent(USER_AGENT, site)
    emitter = Emitter(max_items)
    handler = KolonialHandlers(site, emitter)
    http_client = HttpClient(USER_AGENT, minimum_wait, maximum_wait)
    crawler = Crawler(robot_agent, http_client, handler)

    queue = asyncio.Queue()
    queue.put_nowait("/")

    workers = [
        asyncio.create_task(worker_task(n, crawler, queue)) for n in range(concurrent)
    ]
    await queue.join()

    for worker in workers:
        worker.cancel()

    await asyncio.gather(*workers, return_exceptions=True)
    await http_client.close()

    end_time = time.time()
    print(f"{http_client.gets} requests")
    print(f"{emitter.count} entries")
    print(f"took {end_time - start_time}s")


def empty_queue(queue):
    for _ in range(queue.qsize()):
        queue.get_nowait()
        queue.task_done()


async def worker_task(n, crawler, queue):
    while True:
        link = await queue.get()

        new_links = await crawler.crawl(link)
        for link in new_links:
            queue.put_nowait(link)

        queue.task_done()

        if crawler.link_handlers.emitter.enough():
            empty_queue(queue)
            return


class HttpClient:
    def __init__(self, user_agent, minimum_wait, maximum_wait):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": user_agent}, raise_for_status=True
        )
        self.minimum_wait = minimum_wait
        self.maximum_wait = maximum_wait 
        self.gets = 0

    async def get(self, url):
        await asyncio.sleep(random.uniform(self.minimum_wait, self.maximum_wait))
        self.gets += 1
        response = await self.session.get(url)
        async with response:
            return Response(status_code=response.status, text=await response.text())

    async def close(self):
        await self.session.close()


class Emitter:
    def __init__(self, max_items):
        self.count = 0
        self.max_items = max_items

    def emit(self, product):
        self.count += 1
        print(product)

    def enough(self):
        return self.count >= self.max_items


def create_robot_agent(user_agent, site):
    r = Robots.fetch(f"{site}/robots.txt")
    return r.agent(user_agent)


