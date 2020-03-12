from .scraper import UtappdScraper


class UntappdClient:
    """A facade class used for untappd"""

    def __init__(self, parser: UtappdScraper):
        self._parser = parser

    def search_beer(self, beer_name):
        """Performs searching beers by name"""
        options = {"query": beer_name, "search_type": "beer", "sort": "all"}
        result = self._parser.search(**options)
        beers = result.get("entities", {}).values()
        return beers

    def get_beer(self, beer_id: int):
        return self._parser.get_beer(beer_id)

    def get_brewery(self, beer_id: int):
        pass

    def get_similar(self, beer_id: int):
        pass

    def get_locations(self, beer_id: int):
        pass


__all__ = ["UntappdClient"]
