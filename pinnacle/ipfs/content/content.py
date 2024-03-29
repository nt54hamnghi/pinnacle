import mimetypes
import posixpath
from io import UnsupportedOperation
from typing import cast
from typing import IO
from typing import Literal

import anyio
from anyio import AsyncFile

from pinnacle.type_aliases import PathType


class UnsupportedSubdomainGateway(Exception):
    def __init__(self) -> None:
        super().__init__("Gateway doesn't support subdomain type")


class InvalidGatewayException(ValueError):
    def __init__(self) -> None:
        super().__init__(
            'Invalid gateway option. Available option: ["path", "subdomain"]'
        )


class Gateway:
    def __init__(
        self,
        gatewayURL: str,
        is_subdomain_supported: bool = False,
        scheme: Literal["https", "http"] = "http",
    ) -> None:
        self.gatewayURL = gatewayURL
        self.is_subdomain_supported = is_subdomain_supported
        self.scheme = scheme

    def path_gateway(self, cid: str):
        return f"{self.scheme}://{self.gatewayURL}/ipfs/{cid}/"

    def subdomain_gateway(self, cid: str):
        if not self.is_subdomain_supported:
            raise UnsupportedSubdomainGateway
        return f"{self.scheme}://{cid}.ipfs.{self.gatewayURL}/"

    def gateway(
        self,
        cid: str,
        option: Literal["path", "subdomain"] = "subdomain",
    ):
        if option == "path":
            return self.path_gateway(cid)
        elif option == "subdomain":
            return self.subdomain_gateway(cid)
        else:
            raise InvalidGatewayException


SUBDOMAIN_SUPPORTED_GATEWAYS = {
    "local": Gateway("localhost:8080", True),
    "ipfs": Gateway("ipfs.io", True, "https"),
    "nftstorage": Gateway("nftstorage.link", True, "https"),
    "w3s": Gateway("w3s.link", True, "https"),
}

GATEWAYS = {
    "local_ip": Gateway("127.0.0.1:8080"),
    "pinata": Gateway("gateway.pinata.cloud", scheme="https"),
}

GATEWAYS_STORE = GATEWAYS | SUBDOMAIN_SUPPORTED_GATEWAYS


GatewayName = Literal["local", "local_ip", "ipfs", "nftstorage", "pinata", "w3s"]


class BaseContent:
    def __init__(self, path: PathType) -> None:
        self.path = path
        self.is_pinned = False
        self.cid: str | None = None

        self._gateway: Gateway | None = None
        self._file: IO[bytes] | AsyncFile[bytes] | None = None
        self._bytes: bytes | None = None

        self._mimetype = "application/octet-stream"
        self._mimetype_set = False

    @property
    def basename(self) -> str:
        return posixpath.basename(self.path)

    @property
    def opened(self):
        return self._file is not None

    @property
    def closed(self):
        return self._file is not None and self._file.closed

    @property
    def mimetype(self) -> str:
        if self._mimetype_set:
            return self._mimetype
        guess, _ = mimetypes.guess_type(self.basename)

        return guess or self._mimetype

    @mimetype.setter
    def mimetype(self, value: str):
        self._mimetype = value
        self._mimetype_set = True

    @property
    def uri(self):
        """Gateway-agnostic URI"""
        if not self.is_pinned or self.cid is None:
            raise ValueError("Content is not pinned yet")

        return f"ipfs://{self.cid}"

    def set_pinned_status(self, cid: str):
        self.is_pinned = True
        self.cid = cid

    def _prepare(self):
        """Prepare the content for pinning request"""

        if self._bytes is None:
            raise ValueError("Content's bytes has not been read")

        return dict(
            content=self._bytes,
            headers={"Content-Type": self.mimetype},
        )

    def _prepare_multipart(self, include_mimetype: bool = False):
        """Prepare the content for MULTIPART pinning request"""

        if self._bytes is None:
            raise ValueError("Content's bytes has not been read")

        if include_mimetype:
            files = {"file": (self.basename, self._bytes, self.mimetype)}
        else:
            files = {"file": (self.basename, self._bytes)}  # type: ignore

        return dict(files=files)

    def add_gateway(self, gateway: Gateway):
        """Register a new gateway to use when calling get_gateway"""
        self._gateway = gateway

    def remove_gateway(self):
        self._gateway = None

    def get_gateway(
        self,
        *,
        name: GatewayName = "ipfs",
        type: Literal["path", "subdomain"] = "path",
    ):
        """Generate an IPFS-compatible url to view content"""
        if not self.is_pinned or self.cid is None:
            raise ValueError("Content is not pinned yet")

        if self._gateway is not None:
            return self._gateway.gateway(self.cid, type)

        try:
            gateway = GATEWAYS_STORE[name]
        except KeyError:
            raise ValueError(f"Invalid gateway. Available: {GATEWAYS_STORE.keys}")
        else:
            return gateway.gateway(self.cid, type)


class Content(BaseContent):
    """Content Object with IPFS object properties."""

    def open(self):
        if self.opened:
            raise UnsupportedOperation("Content is already opened")

        self._file = open(self.path, "rb")
        self._bytes = self._file.read()
        return self

    def close(self):
        if not self.opened:
            raise UnsupportedOperation("Content is not yet opened")

        cast(IO[bytes], self._file).close()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_instance, traceback):
        self.close()
        # depending on whether an exception was raised or not (in the with block)
        # True: exception did not happen or had been handled, no need to re-raise
        # False: re-raise the exception
        return exc_instance is None


class AsyncContent(BaseContent):
    """Content Object with IPFS object properties."""

    async def open(self):
        if self.opened:
            raise UnsupportedOperation("Content is already opened")

        self._file = await anyio.open_file(self.path, "rb")
        self._bytes = await self._file.read()
        return self

    async def close(self):
        if not self.opened:
            raise UnsupportedOperation("Content is not yet opened")

        await cast(AsyncFile[bytes], self._file).aclose()

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc_instance, traceback):
        await self.close()
        return exc_instance is None
