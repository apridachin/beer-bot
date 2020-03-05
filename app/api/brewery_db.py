import urllib.parse
from requests import request
from app.settings import BreweryToken


class BeerClient:
    def __init__(self, timeout, testing=False):
        self._url = 'https://sandbox-api.brewerydb.com/v2' if testing else 'https://api.brewerydb.com/v2'
        self._timeout = timeout

    @staticmethod
    def _convert(value: bool):
        return 'Y' if value else 'N'

    def check(self):
        url = f'{self._url}/heartbeat&key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        return json['data']

    def search_beer(self, value: str):
        q = urllib.parse.urlencode(value)
        url = f'{self._url}/search?type=beer&q={q}&key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        beers = []
        if json['totalResults'] == 0:
            return beers
        for raw_beer in json['data']:
            beer = BeerClient.parse_beer(raw_beer)
            beers.append(beer)
        return beers

    def search_brewery(self, value: str):
        q = urllib.parse.urlencode(value)
        url = f'{self._url}/search?type=brewery&q={q}&key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        breweries = []
        if json['totalResults'] == 0:
            return breweries
        for raw_beer in json['data']:
            beer = BeerClient.parse_beer(raw_beer)
            breweries.append(beer)
        return breweries

    def get_random(self, with_social=True, with_ingredients=True, with_breweries=True):
        url = f'{self._url}/beer/random?' \
              f'withSocialAccounts={BeerClient._convert(with_social)}&' \
              f'withIngredients={BeerClient._convert(with_ingredients)}&' \
              f'withBreweries={BeerClient._convert(with_breweries)}&' \
              f'key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        beer = BeerClient.parse_beer(data.get('data', {}))
        return beer

    def get_by_id(self, id: int, with_social=True, with_ingredients=True, with_breweries=True):
        qid = urllib.parse.urlencode(id)
        url = f'{self._url}/beer/{qid}?' \
              f'withSocialAccounts={BeerClient._convert(with_social)}&' \
              f'withIngredients={BeerClient._convert(with_ingredients)}&' \
              f'withBreweries={BeerClient._convert(with_breweries)}&' \
              f'key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        beer = BeerClient.parse_beer(data.get('data', {}))
        return beer

    def get_by_name(self, name: str, with_social=True, with_ingredients=True, with_breweries=True):
        qname = urllib.parse.urlencode(name)
        url = f'{self._url}/beers?name={qname}&' \
              f'withSocialAccounts={BeerClient._convert(with_social)}&' \
              f'withIngredients={BeerClient._convert(with_ingredients)}&' \
              f'withBreweries={BeerClient._convert(with_breweries)}&' \
              f'key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        beers = []
        if json.get('totalResults', 0) == 0:
            return beers
        for raw_beer in json.get('data', []):
            beer = BeerClient.parse_beer(raw_beer)
            beers.append(beer)
        return beers

    def get_adjuncts(self, beer_id: str):
        qid = urllib.parse.urlencode(beer_id)
        url = f'{self._url}/beer/{qid}/adjuncts?key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        return json['data']

    def get_ingredients(self, beer_id: str):
        qid = urllib.parse.urlencode(beer_id)
        url = f'{self._url}/beer/{qid}/ingredients?key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        return json['data']

    def get_variations(self, beer_id: str):
        qid = urllib.parse.urlencode(beer_id)
        url = f'{self._url}/beer/{qid}/variations?key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        return json['data']

    def get_styles(self):
        url = f'{self._url}/styles?key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        return json['data']

    def get_style_by_id(self, style_id: str):
        qid = urllib.parse.urlencode(style_id)
        url = f'{self._url}/styles/{qid}?key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        return json['data']

    @staticmethod
    def parse_beer(data):
        beer_id = data.get('id', '')
        name = data.get('name', '')
        abv = data.get('abv', None)
        ibu = data.get('ibu', None)
        description = data.get('style', {}).get('description', '')
        style = data.get('style', {}).get('name', '')
        category = data.get('style', {}).get('category', {}).get('name')
        raw_accounts = data.get('socialAccounts', [])
        raw_breweries = data.get('breweries', [])

        breweries = []
        for raw_b in raw_breweries:
            brewerie_name = raw_b.get('name', '')
            is_working = raw_b.get('isInBusiness', 'N')
            is_verified = raw_b.get('isVerified', 'N')
            brewerie = {
                'name': brewerie_name,
                'is_working': is_working,
                'is_verified': is_verified
            }
            breweries.append(brewerie)

        accounts = []
        for raw_account in raw_accounts:
            media_name = raw_account.get('socialMedia', {}).get('name', '')
            website = raw_account.get('socialMedia', {}).get('website', '')
            link = raw_account.get('link', '')
            account = {
                'name': media_name,
                'website': website,
                'link': link
            }
            accounts.append(account)

        beer = {
            'id': beer_id,
            'name': name,
            'abv': abv,
            'ibu': ibu,
            'style': style,
            'category': category,
            'description': description,
            'accounts': accounts,
            'breweries': breweries
        }

        return beer


__all__ = ['BeerClient']
