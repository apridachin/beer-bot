from app import logging, settings
from app.api.brewery_db import BeerClient
from app.bot.beer_bot import BeerBot

logging.init_app()

beer_client = BeerClient(timeout=10)
beer_bot = BeerBot(client=beer_client)


__all__ = ["beer_bot"]
