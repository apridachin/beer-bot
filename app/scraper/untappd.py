import re
import sys
import traceback
from operator import itemgetter
from pprint import pprint

from bs4 import BeautifulSoup

from app.utils.fetch import simple_get


class UtappdScraper:
    def __init__(self):
        self.url = "https://untappd.com"

    def search(self, options):
        query, search_type, sort = itemgetter("query", "type", "sort")(options)
        url = f"{self.url}/search?q={query}&type={search_type}&sort={sort}"
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        # todo parse function choice
        result = self.parse_search(response)
        return result

    def get_beer(self, beer_id: int):
        url = f"{self.url}/beer/{beer_id}"
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        result = UtappdScraper.parse_beer(response)
        return result

    def get_brewery(self, brewery_id: int):
        url = f"{self.url}/brewery/{brewery_id}"
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        result = UtappdScraper.parse_brewery(response)
        return result

    def parse_search(self, response):
        search_result = {"total": 0, "entities": {}}

        html = BeautifulSoup(response, "html.parser")
        total_text = html.find("p", class_="total").text.strip()
        total = UtappdScraper.convert_to_float(total_text)
        results = html.find_all("div", class_="beer-item")

        for r in results:
            try:
                beer_text = r.find("a", class_="label")["href"].strip()
                beer_id = int(re.sub(r"\D", "", beer_text))
                beer = self.get_beer(beer_id)

                search_result["entities"].update({beer_id: beer})
            except Exception:
                # todo log error
                traceback.print_exc(file=sys.stdout)

        search_result.update({"total": total})
        return search_result

    @staticmethod
    def parse_beer(response):
        html = BeautifulSoup(response, "html.parser")

        name = html.find("h1").text.strip()
        brewery_name = html.find("p", class_="brewery").text.strip()
        brewery_link = (
            html.find("p", class_="brewery").find("a")["href"].replace("/", "").strip()
        )
        style = html.find("p", class_="style").text.strip()
        abv_text = html.find("p", class_="abv").text.strip()
        abv = UtappdScraper.convert_to_float(abv_text)
        ibu_text = html.find("p", class_="ibu").text.strip()
        ibu = UtappdScraper.convert_to_float(ibu_text)
        rating_text = html.find("div", class_="caps")["data-rating"].strip()
        rating = UtappdScraper.convert_to_float(rating_text)  # todo fix float convert
        raters = (
            html.find("p", class_="raters")
            .text.replace("Ratings", "")
            .replace(",", "")
            .strip()
        )
        description = html.find("div", class_="beer-descrption-read-less").text.strip()
        # add brewery parsing
        beer = {}
        beer.update(
            {
                "name": name,
                "brewery": {"name": brewery_name, "link": brewery_link},
                "style": style,
                "abv": abv,
                "ibu": ibu,
                "rating": rating,
                "raters": raters,
                "description": description,
            }
        )
        return beer

    @staticmethod
    def parse_brewery(response):
        html = BeautifulSoup(response, "html.parser")

        name = html.find("h1").text.strip()
        location = html.find("p", class_="brewery").text.strip()
        style = html.find("p", class_="style").text.strip()
        rating = html.find("div", class_="caps")["data-rating"].strip()
        raters = (
            html.find("p", class_="raters")
            .text.replace("Ratings", "")
            .replace(",", "")
            .strip()
        )
        beers_count = html.find("p", class_="count").text.strip()

        entity = {}
        entity.update(
            {
                "name": name,
                "location": location,
                "style": style,
                "rating": rating,
                "raters": raters,
                "beers_count": beers_count,
            }
        )
        return entity

    @staticmethod
    def convert_to_float(text):
        string = re.sub(r"[^\d\.]", "", text)
        result = float(string) if string else 0
        return result


def test_run():
    default_options = {"query": "kek", "type": "beer", "sort": "all"}
    scraper = UtappdScraper()
    result = scraper.search(default_options)
    pprint(result)


__all__ = ["UtappdScraper", "test_run"]
