import json
from redis.exceptions import RedisError
from dataclasses import asdict

from app.logging import LoggerMixin
from app.entities import Beer, Brewery


class RedisCache(LoggerMixin):
    def __init__(self, redis):
        super().__init__()
        self._cache = redis

    def get_from_cache(self, key: str):
        """Get item from redis cache and prepare it for bot"""
        self.logger.info(f"Check redis cache {key}")
        result = None
        try:
            response = self._cache.get(key)
            if response is not None:
                result = self.prepare_response(key, response)
        except RedisError as e:
            result = None
            self.logger.error(f"Can't connect to redis cache: {e}")
        finally:
            return result

    def set_to_cache(self, key: str, value):
        """Set entity item to redis cache"""
        result: bool = False
        try:
            cache_value = json.dumps(asdict(value))
            result = self._cache.set(key, cache_value)
            self.logger.info(f"Set redis cache {key} {value} {result}")
        except RedisError as e:
            self.logger.error(f"Redis error: {e}")
        finally:
            return result

    def prepare_response(self, key, response):
        self.logger.info(f"Try to parse redis response {response}")
        result = None
        try:
            if key.startswith("beer"):
                result = self.prepare_beer(response)
            elif key.startswith("brewery"):
                result = self.prepare_brewery(response)
            else:
                result = response
            self.logger.info(f"Parse redis response successfully {result}")
        except AttributeError as e:
            self.logger("Can't parse redis response")
        finally:
            return result

    def prepare_beer(self, response) -> Beer:
        """Preparing beer entity for bot"""
        beer = json.loads(response)
        brewery = beer["brewery"]
        similar = beer["similar"]
        result = Beer(**beer)
        result.set_brewery(brewery)
        result.set_similar(similar)
        return result

    def prepare_brewery(self, response) -> Brewery:
        """Preparing brewery entity for bot"""
        brewery = json.loads(response)
        location = brewery["location"]
        contact = brewery["contact"]
        result = Brewery(**brewery)
        result.set_location(location)
        result.set_contact(contact)
        return result


__all__ = ["RedisCache"]
