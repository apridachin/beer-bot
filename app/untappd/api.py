from typing import Callable

from aiohttp import ClientSession

from app.logging import LoggerMixin
from app.settings import UntappdID, UntappdToken
from app.utils.fetch import async_fetch
from app.types import BreweryAPIShort, ContactAPI, LocationAPI, BeerAPI, SimilarAPI, SimilarAPIList, BreweryAPI


class UntappdAPI(LoggerMixin):
    """ API client for Untappd.com """

    base_url = "https://api.untappd.com/v4"
    client_id = UntappdID
    client_token = UntappdToken

    async def search_beer(self, query, limit: int = 1):
        url = (
            f"{UntappdAPI.base_url}/search/beer?q={query}&client_id={UntappdAPI.client_id}&client_secret={UntappdToken}"
        )
        beers = []
        async with ClientSession() as session:
            response = await async_fetch(session, url)
            beers = await self._parse_beer_search(response, limit=limit)
        return beers

    async def search_brewery(self, query):
        url = f"{UntappdAPI.base_url}/search/brewery?q={query}&client_id={UntappdAPI.client_id}&client_secret={UntappdToken}"
        breweries = []
        async with ClientSession() as session:
            response = await async_fetch(session, url)
            breweries = self._parse_brewery_search(response, limit=1)
        return breweries

    async def get_beer(self, beer_id):
        url = f"https://api.untappd.com/v4/beer/info/{beer_id}?client_id={UntappdAPI.client_id}&client_secret={UntappdToken}"
        beer = {}
        async with ClientSession() as session:
            response = await async_fetch(session, url)
            raw_beer = response["response"]["beer"]
            beer = self._parse_beer(raw_beer)
        return beer

    async def get_brewery(self, brewery_id: int) -> BreweryAPI:
        url = f"https://api.untappd.com/v4/brewery/info/{brewery_id}?client_id={UntappdAPI.client_id}&client_secret={UntappdToken}"
        brewery = {}
        async with ClientSession() as session:
            response = await async_fetch(session, url)
            raw_brewery = response["response"]["brewery"]
            brewery = self._parse_brewery(raw_brewery)
        return brewery

    async def get_brewery_by_beer(self, beer_id: int) -> BreweryAPI:
        beer = await self.get_beer(beer_id)
        brewery_id = beer.brewery.id
        brewery = await self.get_brewery(brewery_id)
        return brewery

    def get_similar(self, beer_id):
        pass

    def get_locations(self, beer_id):
        pass

    async def _parse_beer_search(self, response, limit: int = 3):
        result = []
        try:
            self.logger.info(f"Try to parse response {response}")
            beers = response["response"]["beers"]["items"]
            for beer in beers[0:limit]:
                beer_id = beer["beer"]["bid"]
                item = await self.get_beer(beer_id)
                result.append(item)
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
        finally:
            self.logger.info(f"Successfully parse response {response}")
            return result

    async def _parse_brewery_search(self, response, limit: int = 3):
        result = []
        try:
            self.logger.info(f"Try to parse response {response}")
            breweries = response["response"]["brewery"]["items"]
            for brewery in breweries[0:limit]:
                brewery_id = brewery["brewery_id"]
                item = self.get_brewery(brewery_id)
                result.append(item)
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
        finally:
            self.logger.info(f"Successfully parse response {response}")
            return result

    def _parse_beer(self, raw_beer):
        result = None
        try:
            self.logger.info(f"Try to parse response {raw_beer}")
            brewery = self._parse_beer_brewery(raw_beer["brewery"])
            similar = self._parse_similar(raw_beer["similar"]["items"])
            result = BeerAPI(
                id=raw_beer["bid"],
                name=raw_beer["beer_name"],
                style=raw_beer["beer_style"],
                abv=raw_beer["beer_abv"],
                ibu=raw_beer["beer_ibu"],
                rating=raw_beer["rating_score"],
                raters=raw_beer["rating_count"],
                description=raw_beer["beer_description"],
                brewery=brewery,
                similar=similar,
            )
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
        finally:
            self.logger.info(f"Successfully parse response {result}")
            return result

    def _parse_beer_brewery(self, raw_brewery) -> BreweryAPIShort:
        result = None
        try:
            self.logger.info(f"Try to parse beer brewery {raw_brewery}")
            result = BreweryAPIShort(id=raw_brewery["brewery_id"], name=raw_brewery["brewery_name"],)
        except AttributeError as e:
            self.logger.error(f"Can not parse beer brewery, error: {e}")
        finally:
            self.logger.info(f"Successfully parse beer brewery {result}")
            return result

    def _parse_similar(self, similar: []) -> SimilarAPIList:
        result = []
        try:
            for s in similar:
                self.logger.info(f"Try to parse beer brewery {s}")
                item = SimilarAPI(id=s["beer"]["bid"], name=s["beer"]["beer_name"])
                result.append(item)
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error: {e}")
        finally:
            self.logger.info(f"Successfully parse similar beers {result}")
            return result

    def _parse_brewery(self, raw_brewery):
        result = None
        try:
            self.logger.info(f"Try to parse brewery {raw_brewery}")
            raw_contact = raw_brewery["contact"]
            raw_location = raw_brewery["location"]
            result = BreweryAPI(
                id=raw_brewery["brewery_id"],
                name=raw_brewery["brewery_name"],
                contact=ContactAPI(
                    twitter=raw_contact["twitter"], facebook=raw_contact["facebook"], url=raw_contact["url"],
                ),
                location=LocationAPI(lat=raw_location["brewery_lat"], lng=raw_location["brewery_lng"]),
                brewery_type=raw_brewery["brewery_type"],
                brewery_type_id=raw_brewery["brewery_type_id"],
                country=raw_brewery["country_name"],
                rating=raw_brewery["rating"]["rating_score"],
                raters=raw_brewery["rating"]["count"],
                description=raw_brewery["brewery_description"],
            )
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
        finally:
            self.logger.info(f"Successfully parse brewery {result}")
            return result

    async def _get(self, url, parse_func: Callable):
        async with ClientSession() as session:
            response = await async_fetch(session, url)
            return parse_func(response)
