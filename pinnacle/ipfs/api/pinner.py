from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Callable

import httpx
import psutil

CidGetter = Callable[[httpx.Response], str]
Validator = Callable[..., None]


def ipfs_daemon_active() -> bool:
    """Check if ipfs daemon is running"""
    return "ipfs daemon" in {p.name() for p in psutil.process_iter()}


class NoIPFSDaemon(psutil.Error):
    pass


class CidNotFound(KeyError):
    pass


@dataclass
class Pin:
    url: str
    getter: CidGetter
    keyname: str | None = None
    content_type: str = "application/octet-stream"
    validators: Iterable[Validator] = field(
        kw_only=True, default_factory=tuple
    )

    def validate(self):
        for validator in self.validators:
            validator()

    def get_cid(self, response: httpx.Response) -> str:
        return self.getter(response)


def Local() -> Pin:
    """A wrapper around Pin for Local pinning"""

    url = "http://127.0.0.1:5001/api/v0/add"

    def _getter(response: httpx.Response) -> str:
        cid = response.json()["Hash"]
        if cid is None:
            raise CidNotFound
        return cid

    def _validator():
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
