from datetime import datetime

import httpx
import psutil
from pydantic import BaseModel, Field

from pinnacle.ipfs.config import Config
from pinnacle.ipfs.content.content import Content
from pinnacle.ipfs.model.model import Delegates, Pin, PinStatus, Status

from .pin_api import AsyncPinAPI, PinAPI


class NoIPFSDaemonError(Exception):
    ...


class LocalPinAddResponse(BaseModel):
    Name: str
    Hash: str
    Size: int = Field(gt=0)
    Bytes: int | None = None


class LocalPinBase:
    global_config = Config()

    @staticmethod
    def ipfs_daemon_active() -> bool:
        """Check if ipfs daemon is running"""
        return "ipfs" in {p.name() for p in psutil.process_iter()}

    def _add(
        self, content: Content, raw_response: httpx.Response
    ) -> PinStatus:
        raw_response.raise_for_status()

        response = LocalPinAddResponse(**raw_response.json())
        content.pinned(response.Hash)

        return PinStatus(
            requestid=response.Hash,
            status=Status.pinned,
            created=datetime.now(),
            pin=Pin(cid=response.Hash, name=content.basename),
            delegates=Delegates.from_list(["localhost"]),
        )


class LocalPin(LocalPinBase, PinAPI):
    def add(
        self,
        content: Content,
        *,
        cid_version: int = 1,
    ):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemonError("IPFS daemon is not running")

        raw = self._post(
            "add",
            files=content.prepare(),
            query_params={"cid-version": cid_version},
        )

        return self._add(content, raw)


class AsyncLocalPin(LocalPinBase, AsyncPinAPI):
    async def add(
        self,
        content: Content,
        *,
        cid_version: int = 1,
    ):
        if not self.ipfs_daemon_active():
            raise NoIPFSDaemonError("IPFS daemon is not running")

        raw = await self._post(
            "add",
            files=content.prepare(),
            query_params={"cid-version": cid_version},
        )

        return self._add(content, raw)
