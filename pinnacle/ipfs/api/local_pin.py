from datetime import datetime

import httpx
import psutil
from pydantic import BaseModel, Field

from ..config import Config
from ..content import Content
from ..model.model import Delegates, Pin, PinStatus, Status
from .pin_api import AsyncPinAPI, PinAPI, transform_response


class NoIPFSDaemonError(Exception):
    ...


class LocalPinAddResponse(BaseModel):
    Name: str
    Hash: str
    Size: int = Field(gt=0)
    Bytes: int | None = None

    @property
    def cid(self):
        return self.Hash


class LocalPinMixin:
    global_config = Config()

    @staticmethod
    def ipfs_daemon_active() -> bool:
        """Check if ipfs daemon is running"""
        return "ipfs" in {p.name() for p in psutil.process_iter()}

    @staticmethod
    def _add(content: Content, raw_response: httpx.Response):
        response = transform_response(raw_response, LocalPinAddResponse)
        content.pinned(response.cid)

        return response


class LocalPin(LocalPinMixin, PinAPI):
    def add(self, content: Content, *, cid_version: int = 1):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemonError("IPFS daemon is not running")

        raw = self._post(
            "add",
            files=content.prepare(),
            query_params={"cid-version": cid_version},
        )

        return self._add(content, raw)


class AsyncLocalPin(LocalPinMixin, AsyncPinAPI):
    async def add(self, content: Content, *, cid_version: int = 1):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemonError("IPFS daemon is not running")

        raw = await self._post(
            "add",
            files=content.prepare(),
            query_params={"cid-version": cid_version},
        )

        return self._add(content, raw)
