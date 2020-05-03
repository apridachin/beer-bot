from app import logging, settings
from app.bot.beer_bot import BeerBot
from app.untappd.client import UntappdClient
from app.untappd.scraper import UntappdScraper
from app.untappd.api import UntappdAPI

logging.init_log()

untapped_scrapper = UntappdScraper(timeout=10)
untappd_api = UntappdAPI()
untapped_client = UntappdClient(scraper=untapped_scrapper, api=untappd_api)
beer_bot = BeerBot(client=untapped_client)


__all__ = ["beer_bot"]
