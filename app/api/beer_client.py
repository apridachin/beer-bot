from requests import request


class BeerClient:
    def __init__(self, timeout):
        self._url = 'https://api.punkapi.com/v2'
        self._timeout = timeout

    def get_by_id(self, id: int):
        url = f'{self._url}/beers/{id}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        beer = data[0]
        return beer

    def get_random(self):
        url = f'{self._url}/beers/random'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        random_beer = data[0]
        return random_beer

    def find_by_name(self, name: str):
        url = f'{self._url}/beers?beer_name={name}'
        response = request('GET', url, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()
        return data


__all__ = ['BeerClient']
