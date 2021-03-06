import re
from typing import Union, Optional, List

from bs4 import BeautifulSoup

from app.entities import (
    SearchResult,
    SearchItem,
    TSearchType,
    Beer,
    Brewery,
    BreweryShort,
    SimilarList,
    Similar,
    Location,
    Contact,
)
from app.logging import LoggerMixin
from app.utils.fetch import simple_get


class UntappdScraper(LoggerMixin):
    """A class used to scrap and parse untappd.com in runtime"""

    def __init__(self, timeout: int) -> None:
        """Init  scrapper with timeout"""
        super().__init__()
        self.url = "https://untappd.com"
        self._timeout = timeout

    def request(self, url):
        self.logger.info(f"Start request for {url}")
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}, "timeout": self._timeout})
        self.logger.info(f"Got response {response} for {url}")
        return response

    def search_beer(self, query: str) -> SearchResult:
        """Performs searching beer"""
        url = f"{self.url}/search?q={query}&type=beer&sort=all"
        response = self.request(url)
        result: SearchResult = self._parse_search_page(response)
        return result

    def search_brewery(self, query: str) -> SearchResult:
        """Performs searching brewery"""
        url = f"{self.url}/search?q={query}&type=brewery&sort=all"
        response = self.request(url)
        result: SearchResult = self._parse_search_page(response)
        return result

    def get_beer(self, beer_id: int) -> Optional[Beer]:
        """Performs getting beers by id"""
        url = f"{self.url}/beer/{beer_id}"
        response = self.request(url)
        result = self._parse_beer_page(beer_id, response)
        return result

    def get_brewery(self, brewery_id: int) -> Optional[Brewery]:
        """Performs getting brewery by id"""
        url = f"{self.url}/brewery/{brewery_id}"
        response = self.request(url)
        result = self._parse_brewery_page(brewery_id, response)
        return result

    def get_brewery_by_beer(self, beer_id: int) -> Optional[Brewery]:
        """Performs getting brewery by beer id"""
        self.logger.info(f"get brewery by beer id {beer_id} request")
        beer = self.get_beer(beer_id)
        brewery_id = beer.brewery.id if isinstance(beer, Beer) and isinstance(beer.brewery, BreweryShort) else 0
        brewery = self.get_brewery(brewery_id)
        self.logger.info(f"get brewery by beer id {beer_id} response")
        return brewery

    def crawl_search_page(self, search_type: TSearchType, response):
        """Crawling search results page by page"""

        html = BeautifulSoup(response, "html.parser")
        search_result: List[Union[Optional[Beer], Optional[Brewery]]] = []

        try:
            results = html.find_all("div", class_="beer-item")
            for r in results:
                item_text = r.find("a", class_="label")["href"].strip()
                item_id = int(re.sub(r"\D", "", item_text))
                if search_type == "beer":
                    beer = self.get_beer(item_id)
                    search_result.append(beer)
                else:
                    brewery = self.get_brewery(item_id)
                    search_result.append(brewery)
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Search for {search_result} was crawled successfully")
        return search_result

    def _parse_search_page(self, response) -> SearchResult:
        """Performs searching beers by name"""
        html = BeautifulSoup(response, "html.parser")
        search_result: SearchResult = []

        try:
            results = html.find_all("div", class_="beer-item")
            for r in results:
                item_text = r.find("a", class_="label")["href"].strip()
                item_id = int(re.sub(r"\D", "", item_text))
                item_name = r.find("p", class_="name").text.strip()
                search_item = SearchItem(item_id, item_name)
                search_result.append(search_item)
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Search page for was parsed successfully")
        return search_result

    def _parse_beer_page(self, beer_id, response) -> Optional[Beer]:
        """Perform parsing untappd beer page"""
        html = BeautifulSoup(response, "html.parser")
        beer = None

        try:
            name = html.find("h1").text.strip()
            brewery_name = html.find("p", class_="brewery").text.strip()
            style = html.find("p", class_="style").text.strip()
            abv_text = html.find("p", class_="abv").text.strip()
            abv = UntappdScraper._convert_to_float(abv_text)
            ibu_text = html.find("p", class_="ibu").text.strip()
            ibu = UntappdScraper._convert_to_float(ibu_text)
            rating_text = html.find("div", class_="caps")["data-rating"].strip()
            rating = UntappdScraper._convert_to_float(rating_text)
            raters_text = html.find("p", class_="raters").text.replace("Ratings", "").replace(",", "").strip()
            raters = UntappdScraper._convert_to_float(raters_text)
            description = html.find("div", class_="beer-descrption-read-less").text.strip()
            similar_beer_items = html.find("h3", text="Similar Beers").parent.find_all(
                "a", {"data-href": ":beer/similar"}
            )
            similar: SimilarList = list(map(UntappdScraper._parse_similar_beer, similar_beer_items))

            # todo fix brewery id
            brewery = BreweryShort(id=0, name=brewery_name)
            beer = Beer(
                id=beer_id,
                name=name,
                style=style,
                abv=abv,
                ibu=ibu,
                rating=rating,
                raters=raters,
                description=description,
                brewery=brewery,
                similar=similar,
            )
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Page for beer {beer_id} was parsed successfully")
        return beer

    def _parse_brewery_page(self, brewery_id: int, response) -> Optional[Brewery]:
        """Perform parsing untappd brewery page"""
        html = BeautifulSoup(response, "html.parser")
        brewery = None

        try:
            name = html.find("h1").text.strip()
            style = html.find("p", class_="style").text.strip()
            desc = html.find("div", class_="beer-descrption-read-less").text.strip()
            rating = html.find("div", class_="caps")["data-rating"].strip()
            rating = UntappdScraper._convert_to_float(rating)
            raters = html.find("p", class_="raters").text.replace("Ratings", "").replace(",", "").strip()
            raters = UntappdScraper._convert_to_int(raters)
            fb_item = html.find("a", class_="fb tip")
            fb = fb_item["href"] if fb_item else ""
            tw_item = html.find("a", class_="tw tip")
            tw = tw_item["href"] if tw_item else ""
            url_item = html.find("a", class_="url tip")
            url = url_item["href"] if url_item else ""

            brewery = Brewery(
                id=brewery_id,
                name=name,
                description=desc,
                brewery_type=style,
                rating=rating,
                raters=raters,
                location=Location(None, None),
                contact=Contact(twitter=tw, facebook=fb, url=url),
                country="",
            )
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Page for brewery {brewery_id} was parsed successfully")
        return brewery

    @staticmethod
    def _parse_similar_beer(item) -> Similar:
        similar_id = UntappdScraper._convert_to_int(item["href"])
        similar_name = item.text.strip()
        return Similar(similar_id, similar_name)

    @staticmethod
    def _convert_to_float(text: str) -> float:
        """Convert text to float"""
        string = re.sub(r"[^\d\.]", "", text)
        result = round(float(string), 2) if string else 0.0
        return result

    @staticmethod
    def _convert_to_int(text: str) -> int:
        """Convert text to float"""
        string = re.sub(r"[^\d\.]", "", text)
        result = int(string) if string else 0
        return result


__all__ = ["UntappdScraper"]
