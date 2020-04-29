import pytest

from app.untappd.scraper import UntappdScraper
from app.entities import Brewery, Beer, BreweryShort


@pytest.mark.integration
class TestUntappdScraper:
    def test_search(self):
        scraper = UntappdScraper(timeout=10)
        result = scraper.search_beer(query="test")
        print(result)

        assert result is not None
        assert result.total is not None
        assert len(result.entities) == 5
        assert result.entities[0].id == 1569404
        assert result.entities[0].name == "Lost In Spice"

    def test_get_beer(self):
        scraper = UntappdScraper(timeout=10)
        result = scraper.get_beer(1569404)

        assert result is not None
        assert result.name == "Lost In Spice"
        assert result.style == "Spiced / Herbed Beer"
        assert isinstance(result, Beer)
        assert type(result.description) is str
        assert isinstance(result.brewery, BreweryShort)

    def test_get_brewery(self):
        scraper = UntappdScraper(timeout=10)
        result = scraper.get_brewery(405662)

        assert result is not None
        assert result.name == "Testbräu"
        assert isinstance(result, Brewery)
