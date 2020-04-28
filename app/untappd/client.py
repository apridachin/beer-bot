from typing import TypeVar, List

import asyncio
from aiohttp.web import HTTPException

from app.types import SearchItem, Beer, Brewery
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

    def search_beer(self, beer_name: str):
        """Performs searching beers by name"""
        result = []
        try:
            result = asyncio.new_event_loop().run_until_complete(self._api.search_beer(query=beer_name))
        except HTTPException:
            result = self._scraper.search_beer(query=beer_name).entities
        finally:
            return result

    def search_brewery(self, brewery_name: str):
        """Performs searching beers by name"""
        result = []
        try:
            result = asyncio.new_event_loop().run_until_complete(self._api.search_brewery(query=brewery_name))
        except HTTPException:
            result = self._scraper.search_brewery(query=brewery_name).entities
        finally:
            return result

    def get_beer(self, beer_id: int) -> Beer:
        result = None
        try:
            result = asyncio.new_event_loop().run_until_complete(self._api.get_beer(beer_id=beer_id))
        except HTTPException:
            result = self._scraper.get_beer(beer_id=beer_id)
        finally:
            return result

    def get_brewery(self, brewery_id: int) -> Brewery:
        result = None
        try:
            result = asyncio.new_event_loop().run_until_complete(self._api.get_brewery(brewery_id=brewery_id))
        except HTTPException:
            result = self._scraper.get_brewery(brewery_id=brewery_id)
        finally:
            return result

    def get_brewery_by_beer(self, beer_id: int) -> Brewery:
        result = None
        try:
            result = asyncio.new_event_loop().run_until_complete(self._api.get_brewery_by_beer(beer_id=beer_id))
        except HTTPException:
            result = self._scraper.get_brewery_by_beer(beer_id=beer_id)
        finally:
            return result


__all__ = ["UntappdClient", "TUntappdClient"]
