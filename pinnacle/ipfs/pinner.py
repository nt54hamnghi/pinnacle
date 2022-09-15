from collections.abc import Iterable
from typing import Callable, NoReturn, Optional

import httpx
import psutil
from attrs import define, field

from pinnacle.aliases.typehint import NoneableStr

CidGetter = Callable[[httpx.Response], str]
Validator = Callable[..., Optional[NoReturn]]


def ipfs_daemon_active() -> bool:
    """Check if there is a running ipfs daemon"""
    return "ipfs" in {p.name() for p in psutil.process_iter()}


class NoIPFSDaemon(psutil.Error):
    pass


# Context
@define(order=False, eq=False)
class Pin:
    url: str
    getter: CidGetter
    keyname: NoneableStr = None
    content_type: str = "application/octet-stream"
    validators: Iterable[Validator] = field(kw_only=True, factory=list)

    def validate(self) -> Optional[NoReturn]:
        for validator in self.validators:
            validator()

    def get_cid(self, response: httpx.Response) -> str:
        return self.getter(response)


def Local() -> Pin:
    """A wrapper around Pin for Local pinning"""

    url = "http://127.0.0.1:5001/api/v0/add"

    def _getter(response: httpx.Response) -> str:
        return response.json()["Hash"]

    def _validator() -> Optional[NoReturn]:
        if not ipfs_daemon_active():
            raise NoIPFSDaemon

    return Pin(url, _getter, validators=[_validator])


def Pinata() -> Pin:
    """A wrapper around Pin for Pinanta pinning"""

    url = "http://127.0.0.1:5001/api/v0/add"
    keyname = "PINATA_KEY"

    def _getter(response: httpx.Response) -> str:
        return response.json()["Hash"]

    return Pin(url, _getter, keyname=keyname)


def NFTStorage() -> Pin:
    """A wrapper around Pin for NFT Storage pinning"""

    url = "https://api.nft.storage/upload"
    keyname = "NFT_STORAGE_KEY"
    content_type = "multipart/form-data"

    def _getter(response: httpx.Response) -> str:
        return response.json()["value"]["cid"]

    return Pin(url, _getter, keyname, content_type)


def Web3Storage() -> Pin:
    """A wrapper around Pin for Web3 Storage pinning"""

    url = "https://api.web3.storage/upload"
    keyname = "WEB3_STORAGE_KEY"
    content_type = "multipart/form-data"

    def _getter(response: httpx.Response) -> str:
        return response.json()["cid"]

    return Pin(url, _getter, keyname, content_type)
