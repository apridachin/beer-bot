from typing import List, Union, Literal, Optional
from dataclasses import dataclass

TNumber = Union[float, int]
TSearchType = Union[Literal["beer"], Literal["brewery"]]


@dataclass(frozen=True)
class SearchItem:
    id: int
    name: str


SearchResult = List[SearchItem]


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


@dataclass()
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

    def set_brewery(self, brewery: {}):
        self.brewery = BreweryShort(**brewery)

    def set_similar(self, similar: []):
        s_list = []
        for item in similar:
            s = Similar(**item)
            s_list.append(s)
        self.similar = s_list


BeerList = List[Beer]


@dataclass
class CrawlResult:
    entities: List[Union[Beer, Brewery]]
    total: TNumber = 0
