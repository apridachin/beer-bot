from typing import TypeVar, List

from app.types import SearchItem, Beer
from app.logging import LoggerMixin
from .scraper import UtappdScraper

TUntappdClient = TypeVar("TUntappdClient", bound="UntappdClient")


class UntappdClient(LoggerMixin):
    """A facade class used for untappd"""

    def __init__(self, parser: UtappdScraper):
        super().__init__()
        self._parser = parser

    def search_beer(self, beer_name: str) -> List[SearchItem]:
        """Performs searching beers by name"""
        result = self._parser.search(query=beer_name, search_type="beer", sort="all")
        beers = result.entities
        return beers

    def get_beer(self, beer_id: int) -> Beer:
        return self._parser.get_beer(beer_id)

    def get_brewery(self, beer_id: int):
        pass

    def get_similar(self, beer_id: int):
        pass

    def get_locations(self, beer_id: int):
        pass


__all__ = ["UntappdClient", "TUntappdClient"]
