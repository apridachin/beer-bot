from typing import TypeVar

import asyncio
from aiohttp.web import HTTPException

from app.types import Beer, Brewery
from app.logging import LoggerMixin
from .scraper import UntappdScraper
from .api import UntappdAPI

TUntappdClient = TypeVar("TUntappdClient", bound="UntappdClient")


class UntappdClient(LoggerMixin):
    """A facade class used for untappd"""

    def __init__(self, api: UntappdAPI, scraper: UntappdScraper):
        super().__init__()
        self._api = api
        self._scraper = scraper

    def perform_action(self, action_name, default_result, *args, **kwargs):
        api_action = getattr(self._api, action_name)
        scrapper_action = getattr(self._scraper, action_name)
        result = default_result
        try:
            result = asyncio.new_event_loop().run_until_complete(api_action(*args, **kwargs))
        except HTTPException:
            result = scrapper_action(*args, **kwargs)
        finally:
            return result

    def search_beer(self, beer_name: str):
        """Performs searching beers by name"""
        return self.perform_action("search_beer", [], beer_name)

    def search_brewery(self, brewery_name: str):
        """Performs searching beers by name"""
        return self.perform_action("search_brewery", [], brewery_name)

    def get_beer(self, beer_id: int) -> Beer:
        return self.perform_action("get_beer", None, beer_id)

    def get_brewery(self, brewery_id: int) -> Brewery:
        return self.perform_action("get_brewery", None, brewery_id)

    def get_brewery_by_beer(self, beer_id: int) -> Brewery:
        return self.perform_action("get_brewery_by_beer", None, beer_id)


__all__ = ["UntappdClient", "TUntappdClient"]
