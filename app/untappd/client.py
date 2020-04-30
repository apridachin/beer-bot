import json
from typing import TypeVar, Literal
from dataclasses import asdict

import asyncio
from aiohttp.web import HTTPException
from redis.exceptions import RedisError

from app.entities import Beer, Brewery
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

    def get_item(self, item_id: int, item_type: TItem):
        result = None
        try:
            key = f"{item_type}_{item_id}"
            result = self.get_from_cache(key)
            if result is None:
                result = self.get_from_api(item_id, item_type)
        except RedisError as e:
            self.logger.error(f"Can't connect to redis cache: {e}")
            result = self.get_from_api(item_id, item_type)
        except HTTPException:
            self.logger.error(f"Can't get {item_type} {item_id}")
        finally:
            return result

    def get_brewery_by_beer(self, beer_id: int) -> Brewery:
        return self.perform_action("get_brewery_by_beer", None, beer_id)

    def get_from_api(self, item_id: int, item_type: TItem):
        self.logger.info(f"Try to get {item_type} from api {item_id}")
        result = self.perform_action(f"get_{item_type}", None, item_id)
        try:
            key = f"{item_type}_{item_id}"
            success = self.set_to_cache(key, result)
            self.logger.info(f"Set redis cache {item_type} {item_id} {success}")
        except RedisError as e:
            self.logger.error(f"Can't connect to redis {e}")
        finally:
            return result

    def get_from_cache(self, key: str):
        self.logger.info(f"Check redis cache {key}")
        result = None
        response = self._cache.get(key)
        if response is not None:
            self.logger.info(f"Try to parse redis response {response}")
            if key.startswith("beer"):
                result = self.prepare_beer(response)
            elif key.startswith("brewery"):
                result = self.prepare_brewery(response)
            else:
                result = response
            self.logger.info(f"Parse redis response successfully {result}")
        return result

    def set_to_cache(self, key, value):
        cache_value = json.dumps(asdict(value))
        return self._cache.set(key, cache_value)

    def prepare_beer(self, response) -> Beer:
        beer = json.loads(response)
        brewery = beer["brewery"]
        similar = beer["similar"]
        result = Beer(**beer)
        result.set_brewery(brewery)
        result.set_similar(similar)
        return result

    def prepare_brewery(self, response) -> Brewery:
        brewery = json.loads(response)
        location = brewery["location"]
        contact = brewery["contact"]
        result = Brewery(**brewery)
        result.set_location(location)
        result.set_contact(contact)
        return result


__all__ = ["UntappdClient", "TUntappdClient"]
