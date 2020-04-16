import pytest
from unittest.mock import patch

from app.untappd.scraper import UntappdScraper
from app.types import Brewery


@pytest.mark.units
class TestUntappdScraper:
    @patch("app.utils.fetch.simple_get")
    def test_search(self, mock_get):
        with open("./tests/mocks/search.html", "r") as f:
            html_string = f.read()
            mock_get.return_value = html_string
            scraper = UntappdScraper(timeout=10)
            result = scraper.search(query="test", search_type="beer", sort="all")
            print(result)

            assert result is not None
            assert result.total is not None
            assert len(result.entities) == 5
            assert result.entities[0].id == 1569404
            assert result.entities[0].name == "Lost In Spice"

    @patch("app.utils.fetch.simple_get")
    def test_get_beer(self, mock_get):
        with open("./tests/mocks/beer.html", "r") as f:
            html_string = f.read()
            mock_get.return_value = html_string
            scraper = UntappdScraper(timeout=10)
            result = scraper.get_beer(1569404)

            assert result is not None
            assert result.name == "Lost In Spice"
            assert result.style == "Spiced / Herbed Beer"
            assert result.abv == 5.2
            assert result.ibu == 18.0
            assert result.rating == 3.24
            assert result.raters == 25117.00
            assert type(result.description) is str
            assert isinstance(result.brewery, Brewery)

    @patch("app.utils.fetch.simple_get")
    def test_get_brewery(self, mock_get):
        with open("./tests/mocks/brewery.html", "r") as f:
            html_string = f.read()
            mock_get.return_value = html_string
            scraper = UntappdScraper(timeout=10)
            result = scraper.get_brewery(405662)

            assert result is not None
            assert result.name == "Testbräu"
            assert result.style == "Nano Brewery"
            assert result.rating == 3.64
            assert result.raters == 733.00
            assert type(result.location) is str
            assert result.beers_count == 13
