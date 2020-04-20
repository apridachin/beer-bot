from typing import List, Union, Literal
from dataclasses import dataclass

TNumber = Union[float, int]
TSearchType = Union[Literal["beer"], Literal["brewery"]]
TSort = Union[Literal["all"]]


@dataclass(frozen=True)
class Brewery:
    name: str
    link: str


@dataclass(frozen=True)
class BreweryFull:
    id: int
    name: str
    style: str
    rating: float
    raters: float
    location: str
    beers_count: float


@dataclass(frozen=True)
class Beer:
    id: str
    name: str
    style: str
    abv: TNumber
    ibu: TNumber
    rating: TNumber
    raters: float
    description: str
    brewery: Brewery
    similar: List[TNumber]


TBeerList = List[Beer]


@dataclass(frozen=True)
class SearchItem:
    id: int
    name: str


@dataclass
class SearchResult:
    entities: List[SearchItem]
    total: TNumber = 0


@dataclass
class CrawlResult:
    entities: List[Union[Beer, BreweryFull]]
    total: TNumber = 0


@dataclass
class ContactAPI:
    twitter: str
    facebook: str
    url: str


@dataclass
class LocationAPI:
    lat: float
    lng: float


@dataclass(frozen=True)
class BreweryAPIShort:
    id: int
    name: str


@dataclass(frozen=True)
class BreweryAPI(BreweryAPIShort):
    brewery_type: str
    brewery_type_id: int
    country: str
    description: str
    contact: ContactAPI
    location: LocationAPI
    rating: float
    raters: int


@dataclass(frozen=True)
class SimilarAPI:
    id: int
    name: str


SimilarAPIList = List[SimilarAPI]


@dataclass(frozen=True)
class BeerAPI(Beer):
    brewery: BreweryAPIShort
    similar: SimilarAPIList


TBeerAPIList = List[BeerAPI]
