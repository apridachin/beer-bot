from typing import TypeVar, Literal

import asyncio
from aiohttp.web import HTTPException

from app.entities import Brewery
from app.logging import LoggerMixin
from .scraper import UntappdScraper
from .api import UntappdAPI

TUntappdClient = TypeVar("TUntappdClient", bound="UntappdClient")
TItem = Literal["beer", "brewery"]


class UntappdClient(LoggerMixin):
    """A facade class used for untappd"""

    def __init__(self, api: UntappdAPI, scraper: UntappdScraper, cache):
        super().__init__()
        self._api = api
        self._scraper = scraper
        self._cache = cache

    def perform_action(self, action_name, default_result, *args, **kwargs):
        """Get item by api of by scraping"""
        api_action = getattr(self._api, action_name)
        scrapper_action = getattr(self._scraper, action_name)
        result = default_result
        try:
            result = asyncio.new_event_loop().run_until_complete(api_action(*args, **kwargs))
        except HTTPException:
            result = scrapper_action(*args, **kwargs)
        finally:
            return result

    def search_item(self, query: str, search_type: TItem):
        """Performs searching items by name"""
        return self.perform_action(f"search_{search_type}", [], query)

    def get_item(self, item_id: int, item_type: TItem):
        """Performs getting items by id with checking cache"""
        result = None
        try:
            key = f"{item_type}_{item_id}"
            result = self._cache.get_from_cache(key)
            if result is None:
                result = self.get_from_api(item_id, item_type)
        except HTTPException:
            self.logger.error(f"Can't get {item_type} {item_id}")
        finally:
            return result

    def get_brewery_by_beer(self, beer_id: int) -> Brewery:
        return self.perform_action("get_brewery_by_beer", None, beer_id)

    def get_from_api(self, item_id: int, item_type: TItem):
        """Get item from API with setting cache"""
        self.logger.info(f"Try to get {item_type} from api {item_id}")
        result = self.perform_action(f"get_{item_type}", None, item_id)
        key = f"{item_type}_{item_id}"
        self._cache.set_to_cache(key, result)
        return result


__all__ = ["UntappdClient", "TUntappdClient"]
