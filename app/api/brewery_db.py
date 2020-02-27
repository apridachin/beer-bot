from requests import request
from app.settings import BreweryToken


class BeerClient:
    def __init__(self, timeout, testing=False):
        self._url = 'https://sandbox-api.brewerydb.com/v2' if testing else 'https://api.brewerydb.com/v2'
        self._timeout = timeout

    def get_random(self):
        url = f'{self._url}/beer/random?withSocialAccounts=Y&withIngredients=Y&withBreweries=Y&key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        beer = BeerClient.parse_beer(data.get('data', {}))
        return beer

    def get_by_id(self, id: int):
        url = f'{self._url}/beer/{id}?withSocialAccounts=Y&withIngredients=Y&withBreweries=Y&key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        beer = BeerClient.parse_beer(data.get('data', {}))
        return beer

    def find_by_name(self, name: str):
        url = f'{self._url}/beers?name={name}&withSocialAccounts=Y&withIngredients=Y&withBreweries=Y&key={BreweryToken}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        json = response.json()
        beers = []
        for raw_beer in json['data']:
            beer = BeerClient.parse_beer(raw_beer)
            beers.append(beer)
        return beers

    @staticmethod
    def parse_beer(data):
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
