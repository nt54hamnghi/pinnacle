from abc import ABC, abstractmethod
from typing import Callable

import httpx
import psutil

from pinnacle.aliases.typehint import NoneableStr


class NoIPFSDaemon(psutil.Error):
    pass


class AbstractPin(ABC):
    # keyname is the key name to load access token.
    # content_type is Content_Type header.

    url: str
    keyname: NoneableStr = None
    content_type: str = "application/octet-stream"

    def validate(self, *args, **kwds):
        """method to pre-validate before pinning"""
        pass

    @abstractmethod
    def get_cid(self, response: httpx.Response) -> str:
        pass


class Pin(AbstractPin):
    """A class for dynamically creating Pin"""

    def __init__(
        self,
        url: str,
        callback: Callable[[httpx.Response], str],
        keyname: NoneableStr = None,
        content_type: str = "application/octet-stream",
        validator: Callable[..., None] = None,
    ) -> None:
        """
        Args:
            callback (Callable[[httpx.Response], str]):
            a callback to handle retrieving cid from a response.

            validator (Callable[..., None], optional):
            a validator to perform any check before pinning. Defaults to None.
        """
        self.url = url
        self.callback = callback
        self.keyname = keyname
        self.content_type = content_type
        self.validator = validator

    def validate(self, *args, **kwds):
        if self.validator is None:
            return
        return self.validator(*args, **kwds)

    def get_cid(self, response: httpx.Response) -> str:
        return self.callback(response)


class LocalPin(AbstractPin):
    """A wrapper around Pin for Local pinning"""

    url = "http://127.0.0.1:5001/api/v0/add"

    @staticmethod
    def ipfs_daemon_active() -> bool:
        """Check if there is a running ipfs daemon"""
        return "ipfs" in {p.name() for p in psutil.process_iter()}

    def validate(self):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemon

    def get_cid(self, response: httpx.Response) -> str:
        return response.json()["Hash"]


class Pinata(AbstractPin):
    """A wrapper around Pin for Pinanta pinning"""

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    keyname = "PINATA_KEY"

    def get_cid(self, response: httpx.Response) -> str:
        return response.json()["IpfsHash"]


class NFTStorage(AbstractPin):
    """A wrapper around Pin for NFT Storage pinning"""

    url = "https://api.nft.storage/upload"
    keyname = "NFT_STORAGE_KEY"
    content_type = "multipart/form-data"

    def get_cid(self, response: httpx.Response) -> str:
        return response.json()["value"]["cid"]


class Web3Storage(AbstractPin):
    """A wrapper around Pin for Web3 Storage pinning"""

    url = "https://api.web3.storage/upload"
    keyname = "WEB3_STORAGE_KEY"
    content_type = "multipart/form-data"

    def get_cid(self, response: httpx.Response) -> str:
        return response.json()["cid"]
