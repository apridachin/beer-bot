from typing import List, Union, Literal, Optional
from dataclasses import dataclass

TNumber = Union[float, int]
TSearchType = Union[Literal["beer"], Literal["brewery"]]


@dataclass(frozen=True)
class SearchItem:
    id: int
    name: str


@dataclass
class SearchResult:
    entities: List[SearchItem]
    total: TNumber = 0


@dataclass
class Contact:
    twitter: Optional[str] = ""
    facebook: Optional[str] = ""
    url: Optional[str] = ""


@dataclass
class Location:
    lat: Optional[float] = None
    lng: Optional[float] = None


@dataclass(frozen=True)
class BreweryShort:
    id: int
    name: str


@dataclass(frozen=True)
class Brewery(BreweryShort):
    brewery_type: str
    country: str
    description: str
    contact: Contact
    location: Location
    rating: float
    raters: int


@dataclass(frozen=True)
class Similar:
    id: int
    name: str


SimilarList = List[Similar]


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
    brewery: BreweryShort
    similar: SimilarList


BeerList = List[Beer]


@dataclass
class CrawlResult:
    entities: List[Union[Beer, Brewery]]
    total: TNumber = 0
