from typing import List, Union

from merakicommons.cache import lazy, lazy_property
from merakicommons.container import searchable

from ...data import Region, Platform
from ..common import CoreData, CassiopeiaObject, CassiopeiaGhost, CoreDataList, CassiopeiaLazyList, get_latest_version, provide_default_region, ghost_load_on
from .common import ImageData, Sprite, Image
from ...dto.staticdata import map as dto


##############
# Data Types #
##############


class MapListData(CoreDataList):
    _dto_type = dto.MapListDto
    _renamed = {"included_data": "includedData"}


class MapData(CoreData):
    _dto_type = dto.MapDto
    _renamed = {"mapId": "id", "mapName": "name", "unpurchasableItemList": "unpurchasableItems", "included_data": "includedData"}

    def __call__(self, **kwargs):
        if "image" in kwargs:
            self.image = ImageData(**kwargs.pop("image"))
        super().__call__(**kwargs)
        return self


##############
# Core Types #
##############


class Maps(CassiopeiaLazyList):
    _data_types = {MapListData}

    @provide_default_region
    def __init__(self, *, region: Union[Region, str] = None, version: str = None, locale: str = None):
        if locale is None and region is not None:
            locale = Region(region).default_locale
        kwargs = {"region": region, "locale": locale}
        if version is not None:
            kwargs["version"] = version
        CassiopeiaObject.__init__(self, **kwargs)

    @lazy_property
    def region(self) -> Region:
        return Region(self._data[MapListData].region)

    @lazy_property
    def platform(self) -> Platform:
        return self.region.platform

    @property
    def version(self) -> str:
        try:
            return self._data[MapListData].version
        except AttributeError:
            version = get_latest_version(region=self.region, endpoint="map")
            self(version=version)
            return self._data[MapListData].version

    @property
    def locale(self) -> str:
        return self._data[MapListData].locale


@searchable({str: ["name", "locale"], int: ["id"]})
class Map(CassiopeiaGhost):
    _data_types = {MapData}

    @provide_default_region
    def __init__(self, *, id: int = None, name: str = None, region: Union[Region, str] = None, version: str = None, locale: str = None):
        if locale is None and region is not None:
            locale = Region(region).default_locale
        kwargs = {"region": region, "locale": locale}
        if version is not None:
            kwargs["version"] = version
        if id is not None:
            kwargs["id"] = id
        if name is not None:
            kwargs["name"] = name
        super().__init__(**kwargs)

    def __get_query__(self):
        query = {"region": self.region, "platform": self.platform, "version": self.version, "locale": self.locale}
        if hasattr(self._data[MapData], "id"):
            query["id"] = self.id
        if hasattr(self._data[MapData], "name"):
            query["name"] = self.name
        return query

    def __eq__(self, other: "Map"):
        if not isinstance(other, Map):
            return False
        q1 = self.__get_query__()
        q2 = other.__get_query__()
        if q1["region"] == q2["region"]:
            if "id" in q1 and "id" in q2:
                if q1["id"] == q2["id"]:
                    return True
            elif "name" in q1 and "name" in q2:
                if q1["name"] == q2["name"]:
                    return True
        else:
            return False

    __hash__ = CassiopeiaGhost.__hash__

    @lazy_property
    def region(self) -> Region:
        return Region(self._data[MapData].region)

    @lazy_property
    def platform(self) -> Platform:
        return self.region.platform

    @property
    def version(self) -> str:
        """The version for this map."""
        try:
            return self._data[MapData].version
        except AttributeError:
            version = get_latest_version(region=self.region, endpoint="map")
            self(version=version)
            return self._data[MapData].version

    @property
    def locale(self) -> str:
        """The locale for this map."""
        return self._data[MapData].locale or self.region.default_locale

    @CassiopeiaGhost.property(MapData)
    @ghost_load_on
    def id(self) -> int:
        """The map's ID."""
        return self._data[MapData].id

    @CassiopeiaGhost.property(MapData)
    @ghost_load_on
    def name(self) -> str:
        return self._data[MapData].name

    @CassiopeiaGhost.property(MapData)
    @ghost_load_on
    def unpurchasable_items(self) -> List[int]:
        return self._data[MapData].unpurchasableItems

    @CassiopeiaGhost.property(MapData)
    @ghost_load_on
    @lazy
    def image(self) -> Image:
        image = Image.from_data(self._data[MapData].image)
        image(version=self.version)
        return image

    @lazy_property
    def sprite(self) -> Sprite:
        return self.image.spriteInfo
