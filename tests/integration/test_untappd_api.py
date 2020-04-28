import pytest
import asyncio

from app.untappd.api import UntappdAPI
from dataclasses import asdict


@pytest.mark.integration
class TestUntappdContracts:
    BEER_ID = 1569404
    BREWERY_ID = 405662

    @staticmethod
    def assert_beer(result):
        assert result is not None
        assert "id" in result
        assert "name" in result
        assert "style" in result
        assert "abv" in result
        assert "ibu" in result
        assert "rating" in result
        assert "raters" in result
        assert "description" in result
        assert "brewery" in result
        assert "similar" in result

    @staticmethod
    def assert_brewery(result):
        assert result is not None
        assert "name" in result
        assert "contact" in result
        assert "location" in result
        assert "rating" in result
        assert "raters" in result
        assert "brewery_type" in result
        assert "description" in result

    @staticmethod
    def assert_similar(result):
        assert result is not None
        assert "id" in result
        assert "name" in result

    def test_search(self):
        client = UntappdAPI()
        response = asyncio.new_event_loop().run_until_complete(client.search_beer(query="test", limit=1))
        result = asdict(response[0])

        TestUntappdContracts.assert_beer(result)
        TestUntappdContracts.assert_similar(result["similar"][0])

    def test_get_beer(self):
        client = UntappdAPI()
        response = asyncio.new_event_loop().run_until_complete(client.get_beer(TestUntappdContracts.BEER_ID))
        result = asdict(response)

        TestUntappdContracts.assert_beer(result)
        TestUntappdContracts.assert_similar(result["similar"][0])

    def test_get_brewery(self):
        client = UntappdAPI()
        response = asyncio.new_event_loop().run_until_complete(client.get_brewery(TestUntappdContracts.BREWERY_ID))
        result = asdict(response)
        TestUntappdContracts.assert_brewery(result)

    def test_get_brewery_by_beer(self):
        client = UntappdAPI()
        response = asyncio.new_event_loop().run_until_complete(client.get_brewery_by_beer(TestUntappdContracts.BEER_ID))
        result = asdict(response)
        TestUntappdContracts.assert_brewery(result)
