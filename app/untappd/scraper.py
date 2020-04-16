import re

from bs4 import BeautifulSoup

from app.types import Beer, Brewery, SearchResult, SearchItem, TSort, TSearchType, CrawlResult, BreweryFull
from app.logging import LoggerMixin
from app.utils.fetch import simple_get


class UntappdScraper(LoggerMixin):
    """A class used to scrap and parse untappd.com in runtime"""

    def __init__(self, timeout: int) -> None:
        """Init  scrapper with timeout"""
        super().__init__()
        self.url = "https://untappd.com"
        self._timeout = timeout

    def search(self, query: str, search_type: TSearchType, sort: TSort) -> SearchResult:
        """Performs searching with options"""
        url = f"{self.url}/search?q={query}&type={search_type}&sort={sort}"
        self.logger.info(f"search beer request {query} {search_type} {sort}")
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}, "timeout": self._timeout})
        self.logger.info(f"search beer response for {query} {search_type} {sort}")
        result: SearchResult = self._parse_search_page(response)
        return result

    def get_beer(self, beer_id: int) -> Beer:
        """Performs getting beers by id"""
        url = f"{self.url}/beer/{beer_id}"
        self.logger.info(f"get beer request {beer_id}")
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        self.logger.info(f"get beer response for {beer_id}")
        result: Beer = self._parse_beer_page(beer_id, response)
        return result

    def get_brewery(self, brewery_id: int) -> BreweryFull:
        """Performs getting brewery by id"""
        url = f"{self.url}/brewery/{brewery_id}"
        self.logger.info(f"get brewery request {brewery_id}")
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        self.logger.info(f"get brewery response for {brewery_id}")
        result: BreweryFull = self._parse_brewery_page(brewery_id, response)
        return result

    def crawl_search_page(self, search_type: TSearchType, response):
        """Crawling search results page by page"""

        html = BeautifulSoup(response, "html.parser")
        search_result = CrawlResult(entities=[])

        try:
            total_text = html.find("p", class_="total").text.strip()
            total = UntappdScraper._convert_to_float(total_text)
            search_result.total = total

            results = html.find_all("div", class_="beer-item")
            for r in results:
                item_text = r.find("a", class_="label")["href"].strip()
                item_id = int(re.sub(r"\D", "", item_text))
                if search_type == "beer":
                    beer = self.get_beer(item_id)
                    search_result.entities.append(beer)
                else:
                    brewery = self.get_brewery(item_id)
                    search_result.entities.append(brewery)
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Search for {search_result} was crawled successfully")
        return search_result

    def _parse_search_page(self, response) -> SearchResult:
        """Performs searching beers by name"""
        html = BeautifulSoup(response, "html.parser")
        search_result = SearchResult(entities=[])

        try:

            total_text = html.find("p", class_="total").text.strip()
            total = UntappdScraper._convert_to_float(total_text)
            search_result.total = total

            results = html.find_all("div", class_="beer-item")
            for r in results:
                item_text = r.find("a", class_="label")["href"].strip()
                item_id = int(re.sub(r"\D", "", item_text))
                item_name = r.find("p", class_="name").text.strip()
                search_item = SearchItem(item_id, item_name)
                search_result.entities.append(search_item)
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Search page for was parsed successfully")
        return search_result

    def _parse_beer_page(self, beer_id, response):
        """Perform parsing untappd beer page"""
        html = BeautifulSoup(response, "html.parser")
        beer = None

        try:
            name = html.find("h1").text.strip()
            brewery_name = html.find("p", class_="brewery").text.strip()
            brewery_link = html.find("p", class_="brewery").find("a")["href"].replace("/", "").strip()
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
            similar_beer_links = set([item["href"] for item in similar_beer_items])
            similar_beers = [int(re.sub(r"\D", "", link)) for link in similar_beer_links]
            location_items = html.find("h3", text=re.compile(".*Verified Locations.*")).parent.find_all(
                "a", {"data-href": ":venue/toplist"}
            )
            locations_links = set([item["href"] for item in location_items])
            locations = [int(re.sub(r"\D", "", location)) for location in locations_links]

            brewery = Brewery(brewery_name, brewery_link)
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
                similar=similar_beers,
                locations=locations,
            )
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Page for beer {beer_id} was parsed successfully")

        return beer

    def _parse_brewery_page(self, brewery_id: int, response) -> BreweryFull:
        """Perform parsing untappd brewery page"""
        html = BeautifulSoup(response, "html.parser")
        brewery = None

        try:
            name = html.find("h1").text.strip()
            location = html.find("p", class_="brewery").text.strip()
            style = html.find("p", class_="style").text.strip()
            rating = html.find("div", class_="caps")["data-rating"].strip()
            rating = UntappdScraper._convert_to_float(rating)
            raters = html.find("p", class_="raters").text.replace("Ratings", "").replace(",", "").strip()
            raters = UntappdScraper._convert_to_float(raters)
            beers_count = html.find("p", class_="count").text.strip()
            beers_count = UntappdScraper._convert_to_float(beers_count)

            brewery = BreweryFull(brewery_id, name, style, rating, raters, location, beers_count)
        except (AttributeError, KeyError) as e:
            self.logger.exception(e)
        else:
            self.logger.info(f"Page for brewery {brewery_id} was parsed successfully")
        return brewery

    @staticmethod
    def _convert_to_float(text: str) -> float:
        """Convert text to float"""
        string = re.sub(r"[^\d\.]", "", text)
        result = round(float(string), 2) if string else 0.0
        return result


__all__ = ["UntappdScraper"]
