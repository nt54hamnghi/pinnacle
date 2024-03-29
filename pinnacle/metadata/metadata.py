import datetime
from enum import auto
from enum import StrEnum
from posixpath import exists
from posixpath import isfile
from typing import Literal

import pydantic
from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl
from pydantic import parse_obj_as

from pinnacle.type_aliases import PathType


class Trail(BaseModel):
    trail_type: str
    value: int | float | str


class DisplayType(StrEnum):
    number = auto()
    boost_percentage = auto()
    boost_number = auto()


class NumberTrail(Trail):
    display_type: DisplayType
    max_value: float | int

    @pydantic.root_validator()
    @classmethod
    def is_value_less_than_max(cls, values):
        value, max = values["value"], values["max_value"]
        if value > max:
            raise ValueError(f"Invalid value of. Cannot be larger than max_value {max}")
        return values


class DateTrail(Trail):
    display_type: Literal["date"] = Field(default="date", const=True)

    @pydantic.validator("value")
    @classmethod
    def is_value_datetime(cls, value):
        result = parse_obj_as(datetime.datetime, value).replace(microsecond=0)
        return int(result.timestamp())


class Metadata(BaseModel):
    """A model following Opensea's attribute standard
    https://docs.opensea.io/docs/metadata-standards
    """

    image: HttpUrl
    name: str
    description: str
    external_url: HttpUrl
    attribute: list[Trail]

    def asdict(self):
        """Serialize Metadata instance (ignore None)."""
        return self.dict(exclude=None)

    def dump(self, filename: PathType):
        with open(filename, "w") as f:
            f.write(self.json(exclude_none=True))

    def save(self, filename: PathType, overwrite: bool = False) -> None:
        """Save metadata"""

        if overwrite:
            self.dump(filename)
        else:
            if exists(filename) and isfile(filename):
                raise FileExistsError
            self.dump(filename)
