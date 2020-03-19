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
    raters: str
    description: str
    brewery: Brewery
    similar: List[TNumber]
    locations: List[TNumber]


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
