import redis

from app import logging, settings
from app.bot.beer_bot import BeerBot
from app.untappd.client import UntappdClient
from app.untappd.scraper import UntappdScraper
from app.untappd.api import UntappdAPI
from app.untappd.cache import RedisCache

logging.init_log()

redis_client = redis.Redis(host=settings.REDIS_URL, port=6379)  # type: ignore

untapped_scrapper = UntappdScraper(timeout=10)
untappd_api = UntappdAPI()
untappd_cache = RedisCache(redis=redis_client)
untapped_client = UntappdClient(scraper=untapped_scrapper, api=untappd_api, cache=redis_client)
beer_bot = BeerBot(client=untapped_client)

__all__ = ["beer_bot"]
