from typing import Optional, List

from app.logging import LoggerMixin
from app.settings import UNTAPPD_ID, UNTAPPD_TOKEN
from app.utils.fetch import async_get
from app.entities import BreweryShort, Contact, Location, Beer, Similar, SimilarList, Brewery, BeerList


class UntappdAPI(LoggerMixin):
    """ API client for Untappd.com """

    base_url = "https://api.untappd.com/v4"
    client_id = UNTAPPD_ID
    client_token = UNTAPPD_TOKEN
    auth_params = f"client_id={client_id}&client_secret={client_token}"

    async def search_beer(self, query, limit: int = 1) -> List[Optional[Beer]]:
        url = f"{UntappdAPI.base_url}/search/beer?q={query}&{UntappdAPI.auth_params}"
        response = await async_get(url)
        beers = await self._parse_beer_search(response, limit=limit)
        return beers

    async def search_brewery(self, query):
        url = f"{UntappdAPI.base_url}/search/brewery?q={query}&{UntappdAPI.auth_params}"
        response = await async_get(url)
        breweries = self._parse_brewery_search(response, limit=1)
        return breweries

    async def get_beer(self, beer_id) -> Optional[Beer]:
        url = f"{UntappdAPI.base_url}/beer/info/{beer_id}?{UntappdAPI.auth_params}"
        response = await async_get(url)
        raw_beer = response["response"]["beer"]
        beer = self._parse_beer(raw_beer)
        return beer

    async def get_brewery(self, brewery_id: int) -> Brewery:
        url = f"{UntappdAPI.base_url}/brewery/info/{brewery_id}?{UntappdAPI.auth_params}"
        response = await async_get(url)
        raw_brewery = response["response"]["brewery"]
        brewery = self._parse_brewery(raw_brewery)
        return brewery

    async def get_brewery_by_beer(self, beer_id: int) -> Brewery:
        beer = await self.get_beer(beer_id)
        brewery_id = beer.brewery.id if isinstance(beer, Beer) and isinstance(beer.brewery, BreweryShort) else 0
        brewery = await self.get_brewery(brewery_id)
        return brewery

    async def _parse_beer_search(self, response, limit: int = 3) -> List[Optional[Beer]]:
        result = []
        try:
            self.logger.info(f"Try to parse response {response}")
            beers = response["response"]["beers"]["items"]
            for beer in beers[0:limit]:
                beer_id = beer["beer"]["bid"]
                item = await self.get_beer(beer_id)
                result.append(item)
            self.logger.info(f"Successfully parse response {response}")
            return result
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
            return []

    async def _parse_brewery_search(self, response, limit: int = 3):
        result = []
        try:
            self.logger.info(f"Try to parse response {response}")
            breweries = response["response"]["brewery"]["items"]
            for brewery in breweries[0:limit]:
                brewery_id = brewery["brewery_id"]
                item = self.get_brewery(brewery_id)
                result.append(item)
            self.logger.info(f"Successfully parse response {response}")
            return result
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
            return []

    def _parse_beer(self, raw_beer) -> Optional[Beer]:
        try:
            self.logger.info(f"Try to parse response {raw_beer}")
            brewery = self._parse_beer_brewery(raw_beer["brewery"])
            similar = self._parse_similar(raw_beer["similar"]["items"])
            result = Beer(
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
            self.logger.info(f"Successfully parse response {result}")
            return result
        except AttributeError as e:
            self.logger.error(f"Can not parse response, error {e}")
            return None

    def _parse_beer_brewery(self, raw_brewery) -> Optional[BreweryShort]:
        try:
            self.logger.info(f"Try to parse beer brewery {raw_brewery}")
            result = BreweryShort(id=raw_brewery["brewery_id"], name=raw_brewery["brewery_name"])
            self.logger.info(f"Successfully parse beer brewery {result}")
            return result
        except AttributeError as e:
            self.logger.error(f"Can not parse beer brewery, error: {e}")
            return None

    def _parse_similar(self, similar: List) -> SimilarList:
        result = []
        try:
            for s in similar:
                self.logger.info(f"Try to parse beer similar {s}")
                item = Similar(id=s["beer"]["bid"], name=s["beer"]["beer_name"])
                result.append(item)
            self.logger.info(f"Successfully parse similar beers {result}")
            return result
        except AttributeError as error:
            self.logger.error(f"Can not parse response, error: {error}")
            return []

    def _parse_brewery(self, raw_brewery):
        try:
            self.logger.info(f"Try to parse brewery {raw_brewery}")
            raw_contact = raw_brewery["contact"]
            raw_location = raw_brewery["location"]
            result = Brewery(
                id=raw_brewery["brewery_id"],
                name=raw_brewery["brewery_name"],
                contact=Contact(
                    twitter=raw_contact["twitter"], facebook=raw_contact["facebook"], url=raw_contact["url"],
                ),
                location=Location(lat=raw_location["brewery_lat"], lng=raw_location["brewery_lng"]),
                brewery_type=raw_brewery["brewery_type"],
                country=raw_brewery["country_name"],
                rating=raw_brewery["rating"]["rating_score"],
                raters=raw_brewery["rating"]["count"],
                description=raw_brewery["brewery_description"],
            )
            self.logger.info(f"Successfully parse brewery {result}")
            return result
        except AttributeError as error:
            self.logger.error(f"Can not parse response, error {error}")
            return None
