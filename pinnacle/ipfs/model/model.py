# generated by datamodel-codegen:
#   filename:  ipfs-pinning-service.yaml
#   timestamp: 2023-04-04T00:52:05+00:00


from datetime import datetime
from enum import StrEnum, auto
from typing import Self

from pydantic import BaseModel, Field


class PinMeta(BaseModel):
    __root__: dict[str, str] | None = None


class Delegates(BaseModel):
    __root__: list[str] = Field(
        example=["/ip4/203.0.113.1/tcp/4001/p2p/QmServicePeerId"],
        max_items=20,
        min_items=1,
        unique_items=True,
        description="List of multiaddrs designated by pinning service that will receive the pin data",  # noqa: E501
    )

    def __iter__(self):
        return iter(self.__root__)

    @classmethod
    def from_list(cls, data: list[str]) -> Self:
        return cls.parse_obj(data)


class Origins(BaseModel):
    __root__: list[str] = Field(
        example=[
            "/ip4/203.0.113.142/tcp/4001/p2p/QmSourcePeerId",
            "/ip4/203.0.113.114/udp/4001/quic/p2p/QmSourcePeerId",
        ],
        max_items=20,
        min_items=0,
        unique_items=True,
        description="List of multiaddrs known to provide the data",
    )

    def __iter__(self):
        return iter(self.__root__)

    @classmethod
    def from_list(cls, data: list[str]) -> Self:
        return cls.parse_obj(data)


class Pin(BaseModel):
    cid: str = Field(
        example="QmCIDToBePinned",
        description="Content Identifier (CID) to be pinned recursively",
    )
    name: str | None = Field(
        None,
        example="PreciousData.pdf",
        max_length=255,
        description="Name for pinned data; can be used for lookups later",
    )
    origins: Origins | None = None
    meta: PinMeta | None = None


class Status(StrEnum):
    queued = auto()
    pinning = auto()
    pinned = auto()
    failed = auto()


class StatusInfo(BaseModel):
    __root__: dict[str, str] | None = None


class PinStatus(BaseModel):
    requestid: str = Field(
        example="UniqueIdOfPinRequest",
        description="Globally unique identifier of the pin request; can be used to check the status of ongoing pinning, or pin removal",  # noqa: E501
    )
    status: Status
    created: datetime = Field(
        example="2020-07-27T17:32:28.276Z",
        description="Immutable timestamp indicating when a pin request entered a pinning service; can be used for filtering results and pagination",  # noqa: E501
    )
    pin: Pin
    delegates: Delegates
    info: StatusInfo | None = None


class PinResults(BaseModel):
    count: int = Field(
        ge=0,
        description="The total number of pin objects for passed query filters",
    )
    results: list[PinStatus] = Field(
        ...,
        max_items=1000,
        min_items=0,
        unique_items=True,
        description="An array of PinStatus results",
    )


class TextMatchingStrategy(StrEnum):
    exact = auto()
    iexact = auto()
    partial = auto()
    ipartial = auto()
