import json
from typing import Any, Optional, Union

from attrs import asdict, define

from pinnacle.aliases.field import noneable, string
from pinnacle.aliases.typehint import GeneralPath, NoneableStr
from pinnacle.ipfs.pin import pin
from pinnacle.ipfs.pinner import AbstractPin


@define(frozen=True, kw_only=True)
class Attribute:
    """A data class following Opensea's attribute standard
    https://docs.opensea.io/docs/metadata-standards
    """

    trait: str = string()
    value: Union[int, float, str]
    display_type: NoneableStr = noneable()

    @display_type.validator
    def _check_display_type(self, attr, val):
        """Validate display type.

        if value is string, display type must be None
        if value is int or float, display type can be:
            "boost_percentage", "boost_number", "number", None
        """
        acceptables = ["boost_percentage", "boost_number", "number", None]

        if isinstance(self.value, str) and val is not None:
            raise TypeError("display type must be None, if value is string")

        if isinstance(self.value, (int, float)) and val not in acceptables:
            raise ValueError(f"Acceptable display types: {acceptables}")


@define(frozen=True, eq=False)
class Metadata:
    """A data class following Opensea's metadata standard
    https://docs.opensea.io/docs/metadata-standards
    """

    name: str = string()
    description: str = string()
    image: str = string()
    external_url: NoneableStr = noneable(kw_only=True)
    attributes: Optional[list[Attribute]] = noneable(kw_only=True)

    def asdict(self) -> dict[str, Any]:
        """Serialize Metadata instance (ignore None)."""
        return asdict(self, filter=lambda _, v: v is not None)

    def save(
        self,
        filename: GeneralPath,
        pinner: Optional[AbstractPin] = None,
    ) -> NoneableStr:
        """Save and pin metadata

        Note: Only pin if pinner is not None
        """

        if not filename.exists():
            with open(filename, "w") as file:
                json.dump(self.asdict(), file, indent=2)

        if pinner:
            token_uri = pin(filename, pinner).gateway()
            return token_uri
