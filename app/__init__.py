from app import logging, settings
from app.api.brewery_db import BeerClient
from app.bot.beer_bot import BeerBot
from app.scraper.untappd import UtappdScraper

logging.init_app()

beer_client = BeerClient(timeout=10)
untapped_scrapper = UtappdScraper(timeout=10)
beer_bot = BeerBot(client=untapped_scrapper)


__all__ = ["beer_bot"]
