from app import logging, settings
from app.bot.beer_bot import BeerBot
from app.untappd.client import UntappdClient
from app.untappd.scraper import UntappdScraper

logging.init_log()

untapped_scrapper = UntappdScraper(timeout=10)
untapped_client = UntappdClient(parser=untapped_scrapper)
beer_bot = BeerBot(client=untapped_client)


__all__ = ["beer_bot"]
