from operator import itemgetter
import scrapy
from scrapy.crawler import CrawlerProcess


class UntappdSpider(scrapy.Spider):
    name = "untappd"
    allowed_domains = ['untappd.com']

    def __init__(self, options=None, *args, **kwargs):
        super(UntappdSpider, self).__init__(*args, **kwargs)
        query, search_type, sort = itemgetter('query', 'type', 'sort')(options)
        self.start_urls = [f'https://untappd.com/search?q={query}&type={search_type}&sort={sort}']

    def parse(self, response):
        self.log('Saved file %s' % response)


# check settings
crawler_process = CrawlerProcess(settings={
    'FEED_FORMAT': 'json',
    'FEED_URI': 'items.json',
})

if __name__ == "__main__":
    default_options = {
        'query': 'test',
        'type': 'beer',
        'sort': 'all'
    }

    crawler_process.crawl(UntappdSpider, options=default_options)
    crawler_process.start()

__all__ = ['crawler_process']
