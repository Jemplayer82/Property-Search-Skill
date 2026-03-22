#!/usr/bin/env python3
"""Search for property deed on tccsearch.org using scrapling"""

from scrapling.spiders import Spider, Request, Response
from scrapling.fetchers import StealthySession
from itemadapter import ItemAdapter
from itemloaders import ItemLoader
from item import Item, Field


class DeedSearchSpider(Spider):
    name = "deed_search"
    start_urls = ["https://tccsearch.org"]
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response: Response):
        self.logger.info(f"Status: {response.status}")
        self.logger.info(f"URL: {response.url}")
        
        # Save the raw HTML
        with open('/home/landon/.openclaw/workspace/tccsearch_raw.html', 'w') as f:
            f.write(response.text)
        
        self.logger.info(f"Response length: {len(response.text)}")
        
        # Try to extract elements
        links = response.css('a::attr(href)').getall()
        forms = response.css('form').getall()
        inputs = response.css('input').getall()
        
        self.logger.info(f"Links found: {len(links)}")
        self.logger.info(f"Forms found: {len(forms)}")
        self.logger.info(f"Inputs found: {len(inputs)}")
        
        yield {"url": response.url, "links": len(links), "forms": len(forms)}


if __name__ == "__main__":
    result = DeedSearchSpider().start()
    print(f"Results: {result}")
