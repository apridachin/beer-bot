import json
from typing import TypeVar
from dataclasses import asdict

import asyncio
from aiohttp.web import HTTPException

from app.entities import Beer, Brewery
from app.logging import LoggerMixin
from .scraper import UntappdScraper
from .api import UntappdAPI

TUntappdClient = TypeVar("TUntappdClient", bound="UntappdClient")


class UntappdClient(LoggerMixin):
    """A facade class used for untappd"""

    def __init__(self, api: UntappdAPI, scraper: UntappdScraper, cache):
        super().__init__()
        self._api = api
        self._scraper = scraper
        self._cache = cache

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
        result = None
        try:
            result = self.get_from_cache(beer_id)
            if result is None:
                self.logger.info(f"Try to get beer from api {beer_id}")
                result = self.perform_action("get_beer", None, beer_id)
                success = self.set_to_cache(beer_id, result)
                self.logger.info(f"Set redis cache {beer_id} {success}")
        except HTTPException:
            self.logger.error(f"Can't get beer {beer_id}")
        finally:
            return result

    def get_brewery(self, brewery_id: int) -> Brewery:
        return self.perform_action("get_brewery", None, brewery_id)

    def get_brewery_by_beer(self, beer_id: int) -> Brewery:
        return self.perform_action("get_brewery_by_beer", None, beer_id)

    def get_from_cache(self, key):
        self.logger.info(f"Check redis cache {key}")
        result = None
        response = self._cache.get(key)
        if response is not None:
            self.logger.info(f"Try to parse redis response {response}")
            result = self.prepare_beer(response)
            self.logger.info(f"Parse redis response successfully {result}")
        return result

    def set_to_cache(self, key, value):
        cache_value = json.dumps(asdict(value))
        return self._cache.set(key, cache_value)

    def prepare_beer(self, response):
        beer_dict = json.loads(response)
        brewery_dict = beer_dict["brewery"]
        similar_list = beer_dict["similar"]
        result = Beer(**beer_dict)
        result.set_brewery(brewery_dict)
        result.set_similar(similar_list)
        return result


__all__ = ["UntappdClient", "TUntappdClient"]
