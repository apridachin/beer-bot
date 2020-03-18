from app import logging, settings
from app.api.brewery_db import BeerClient
from app.bot.beer_bot import BeerBot
from app.untappd.client import UntappdClient
from app.untappd.scraper import UtappdScraper

logging.init_log()

beer_client = BeerClient(timeout=10)
untapped_scrapper = UtappdScraper(timeout=10)
untapped_client = UntappdClient(parser=untapped_scrapper)
beer_bot = BeerBot(client=untapped_client)


__all__ = ["beer_bot"]
