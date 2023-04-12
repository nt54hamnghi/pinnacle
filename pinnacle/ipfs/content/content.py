import posixpath
from typing import IO, Literal, cast

import anyio
from anyio import AsyncFile

from pinnacle.type_aliases import PathType


class Gateway:
    def __init__(self, gatewayURL: str) -> None:
        self.gatewayURL = gatewayURL

    def path_gateway(self, cid: str):
        return f"http://{self.gatewayURL}/ipfs/{cid}/"

    def subdomain_gateway(self, cid: str):
        return f"http://{cid}.ipfs.{self.gatewayURL}/"

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
            raise ValueError(
                'Invalid gateway option. Available option: ["path", "subdomain"]'
            )


GATEWAYS = {
    "local": Gateway("localhost:8080"),
    "local_ip": Gateway("127.0.0.1:8080"),
    "ipfs": Gateway("ipfs.io"),
    "nft_storage": Gateway("nftstorage.link"),
}

GatewayName = Literal["local", "local_ip", "ipfs", "nft_storage"]


class BaseContent:
    def __init__(
        self, path: PathType, mimetype: str = "application/octet-stream"
    ) -> None:
        self.path = path
        self.mimetype = mimetype
        self.is_pinned = False
        self.cid: str | None = None

        self._file: IO[bytes] | AsyncFile[bytes] | None = None
        self._bytes: bytes | None = None

    @property
    def basename(self) -> str:
        return posixpath.basename(self.path)

    @property
    def uri(self):
        """Gateway-agnostic URI"""
        return f"ipfs://{self.cid}"

    def pinned(self, cid: str):
        self.is_pinned = True
        self.cid = cid

    def prepare(self) -> dict[str, tuple[str, bytes]]:
        """Prepare a dict containing fields ready for pinning"""
        if self._bytes is None:
            raise ValueError("Content's bytes has not been read")

        return dict(file=(self.basename, self._bytes))

    def gateway(
        self,
        gateway_name: GatewayName = "ipfs",
        gateway_type: Literal["path", "subdomain"] = "path",
    ):
        """Generate an IPFS-compatible url to view content"""
        if not self.is_pinned:
            raise ValueError("Content is not pinned yet")
        if self.cid is None:
            raise ValueError
        try:
            gateway = GATEWAYS[gateway_name]
        except KeyError:
            raise ValueError(f"Invalid gateway. Available: {GATEWAYS.keys}")
        else:
            return gateway.gateway(self.cid, gateway_type)


class Content(BaseContent):
    """Content Object with IPFS object properties."""

    def open(self):
        if self._file is not None:
            raise ValueError("File is already opened")
        self._file = open(self.path, "rb")
        self._bytes = self._file.read()
        return self

    def close(self):
        if self._file is None:
            raise ValueError("Content is not yet opened")
        cast(IO[bytes], self._file).close()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_instance, traceback):
        self.close()
        # depending on whether an exception was raised or not (in the with block)
        # True: exception did not happend or had been handled, no need to re-raise
        # False: re-raise the exception
        return exc_instance is None


class AsyncContent(BaseContent):
    """Content Object with IPFS object properties."""

    async def open(self):
        if self._file is not None:
            raise ValueError("File is already opened")

        self._file = await anyio.open_file(self.path, "rb")
        self._bytes = await self._file.read()
        return self

    async def close(self):
        if self._file is None:
            raise ValueError("Content is not yet opened")

        await cast(AsyncFile[bytes], self._file).aclose()

    async def __aenter__(self):
        return await self.open()

    async def __aexit__(self, exc_type, exc_instance, traceback):
        await self.close()
        return exc_instance is None
