import httpx
import psutil
from pydantic import BaseModel
from pydantic import Field

from ..config import Config
from ..content import Content
from ..models import Pin
from ..models import PinMeta
from .pin_api import AsyncPinAPI
from .pin_api import PinAPI
from .pin_api import PinMixin


class NoIPFSDaemonError(Exception):
    ...


class LocalPinAdd(BaseModel):
    Name: str
    Hash: str
    Size: int = Field(gt=0)
    Bytes: int | None = None

    @property
    def cid(self):
        return self.Hash


class LocalPinMixin(PinMixin):
    global_config = Config(authless=True)

    @staticmethod
    def ipfs_daemon_active() -> bool:
        """Check if ipfs daemon is running"""
        return "ipfs" in {p.name() for p in psutil.process_iter()}

    def _add(self, content: Content, raw_response: httpx.Response, *args, **kwds):
        response = super()._add(content, raw_response, LocalPinAdd)

        return Pin(
            cid=response.cid,
            name=response.Name,
            meta=PinMeta.from_model(response, exclude={"Name", "Hash"}),
        )


class LocalPin(LocalPinMixin, PinAPI):
    def add(self, content: Content, *, cid_version: int = 1):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemonError("IPFS daemon is not running")

        raw = self._post(
            "add",
            query_params={"cid-version": cid_version},
            **content._prepare_multipart(),
        )

        return self._add(content, raw)


class AsyncLocalPin(LocalPinMixin, AsyncPinAPI):
    async def add(self, content: Content, *, cid_version: int = 1):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemonError("IPFS daemon is not running")

        raw = await self._post(
            "add",
            query_params={"cid-version": cid_version},
            **content._prepare_multipart(),
        )

        return self._add(content, raw)
