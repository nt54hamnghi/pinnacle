import httpx
import psutil
from pydantic import BaseModel, Field

from ..config import Config
from ..content import Content
from .pin_api import AsyncPinAPI, PinAPI, PinMixin


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
    global_config = Config()

    @staticmethod
    def ipfs_daemon_active() -> bool:
        """Check if ipfs daemon is running"""
        return "ipfs" in {p.name() for p in psutil.process_iter()}

    def _add(
        self, content: Content, raw_response: httpx.Response, *args, **kwds
    ):
        return super()._add(content, raw_response, LocalPinAdd)


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
