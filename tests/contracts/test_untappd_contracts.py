import pytest

from app.untappd.scraper import UntappdScraper
from dataclasses import asdict


@pytest.mark.contracts
class TestUntappdContracts:
    def test_search(self):
        scraper = UntappdScraper(timeout=10)
        result = asdict(scraper.search(query="test", search_type="beer", sort="all"))

        assert result is not None
        assert "total" in result
        assert "entities" in result

    def test_get_beer(self):
        scraper = UntappdScraper(timeout=10)
        result = asdict(scraper.get_beer(1569404))

        assert result is not None
        assert "name" in result
        assert "style" in result
        assert "abv" in result
        assert "ibu" in result
        assert "rating" in result
        assert "raters" in result
        assert "description" in result
        assert "brewery" in result

    def test_get_brewery(self):
        scraper = UntappdScraper(timeout=10)
        result = asdict(scraper.get_brewery(405662))

        assert result is not None
        assert "name" in result
        assert "style" in result
        assert "rating" in result
        assert "raters" in result
        assert "location" in result
        assert "beers_count" in result
