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
        result = self.parse_search_page(search_type, response)
        return result

    def search_beer(self, beer_name):
        options = {"query": beer_name, "type": "beer", "sort": "all"}
        result = self.search(options)
        beers = result.get("entities", {}).values()
        return beers

    def get_beer(self, beer_id: int):
        url = f"{self.url}/beer/{beer_id}"
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        result = UtappdScraper.parse_beer_page(response)
        result.update(id=beer_id)
        return result

    def get_brewery(self, brewery_id: int):
        url = f"{self.url}/brewery/{brewery_id}"
        response = simple_get(url, options={"headers": {"User-agent": "BakhusBot"}})
        result = UtappdScraper.parse_brewery_page(response)
        return result

    def parse_search_page(self, search_type, response):
        search_result = {"total": 0, "entities": {}}

        html = BeautifulSoup(response, "html.parser")
        total_text = html.find("p", class_="total").text.strip()
        total = UtappdScraper.convert_to_float(total_text)
        results = html.find_all("div", class_="beer-item")

        for r in results:
            try:
                item_text = r.find("a", class_="label")["href"].strip()
                item_id = int(re.sub(r"\D", "", item_text))
                item_name = r.find("p", class_="name").text.strip()
                search_result["entities"].update({item_id: {"name": item_name, "id": item_id}})
            except Exception:
                # todo log error
                traceback.print_exc(file=sys.stdout)

        search_result.update({"total": total})
        return search_result

    def crawl_search_page(self, search_type, response):
        search_result = {"total": 0, "entities": {}}

        html = BeautifulSoup(response, "html.parser")
        total_text = html.find("p", class_="total").text.strip()
        total = UtappdScraper.convert_to_float(total_text)
        results = html.find_all("div", class_="beer-item")

        for r in results:
            try:
                item_text = r.find("a", class_="label")["href"].strip()
                item_id = int(re.sub(r"\D", "", item_text))
                if search_type == "beer":
                    beer = self.get_beer(item_id)
                    search_result["entities"].update({item_id: beer})
                else:
                    brewery = self.get_brewery(item_id)
                    search_result["entities"].update({item_id: brewery})
            except Exception:
                # todo log error
                traceback.print_exc(file=sys.stdout)

        search_result.update({"total": total})
        return search_result

    @staticmethod
    def parse_beer_page(response):
        html = BeautifulSoup(response, "html.parser")

        name = html.find("h1").text.strip()
        brewery_name = html.find("p", class_="brewery").text.strip()
        brewery_link = html.find("p", class_="brewery").find("a")["href"].replace("/", "").strip()
        style = html.find("p", class_="style").text.strip()
        abv_text = html.find("p", class_="abv").text.strip()
        abv = UtappdScraper.convert_to_float(abv_text)
        ibu_text = html.find("p", class_="ibu").text.strip()
        ibu = UtappdScraper.convert_to_float(ibu_text)
        rating_text = html.find("div", class_="caps")["data-rating"].strip()
        rating = UtappdScraper.convert_to_float(rating_text)  # todo fix float convert
        raters = html.find("p", class_="raters").text.replace("Ratings", "").replace(",", "").strip()
        description = html.find("div", class_="beer-descrption-read-less").text.strip()
        similar_beer_items = html.find("h3", text="Similar Beers").parent.find_all("a", {"data-href": ":beer/similar"})
        similar_beer_links = set([item["href"] for item in similar_beer_items])
        similar_beers = [int(re.sub(r"\D", "", link)) for link in similar_beer_links]
        location_items = html.find("h3", text=re.compile(".*Verified Locations.*")).parent.find_all(
            "a", {"data-href": ":venue/toplist"}
        )
        locations_links = set([item["href"] for item in location_items])
        locations = [int(re.sub(r"\D", "", location)) for location in locations_links]
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
                "similar": similar_beers,
                "locations": locations,
            }
        )
        return beer

    @staticmethod
    def parse_brewery_page(response):
        html = BeautifulSoup(response, "html.parser")

        name = html.find("h1").text.strip()
        location = html.find("p", class_="brewery").text.strip()
        style = html.find("p", class_="style").text.strip()
        rating = html.find("div", class_="caps")["data-rating"].strip()
        raters = html.find("p", class_="raters").text.replace("Ratings", "").replace(",", "").strip()
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
