import json
from datetime import datetime

import httpx
from pydantic import BaseModel, Field

from ...consts import PINATA_SERVICE
from ..config import Config
from ..content import Content
from .pin_api import AsyncPinAPI, PinAPI, PinMixin


class PinataAdd(BaseModel):
    IpfsHash: str = Field(description="IPFS multi-hash for the content")
    PinSize: int = Field(
        description="The pinned content size (in bytes)", gt=0
    )
    Timestamp: datetime = Field(
        description="Timestamp for content pinning (represented in ISO 8601 format)"
    )
    isDuplicate: bool | None = None

    @property
    def cid(self):
        return self.IpfsHash


class PinantaMixin(PinMixin):
    global_config = Config(
        url=PINATA_SERVICE,
        # auth=BearerAuth.from_env("PINATA_JWT"),
    )

    def _add(
        self, content: Content, raw_response: httpx.Response, *args, **kwds
    ):
        return super()._add(content, raw_response, PinataAdd)


class Pinata(PinantaMixin, PinAPI):
    def add(self, content: Content, *, cid_version: int = 1):
        payload = {"pinataOptions": json.dumps({"cidVersion": cid_version})}
        raw = self._post(
            "pinning/pinFileToIPFS",
            data=payload,
            **content._prepare_multipart()
        )

        return self._add(content, raw)


class AsyncPinata(PinantaMixin, AsyncPinAPI):
    async def add(self, content: Content, *, cid_version: int = 1):
        payload = {"pinataOptions": json.dumps({"cidVersion": cid_version})}
        raw = await self._post(
            "pinning/pinFileToIPFS",
            data=payload,
            **content._prepare_multipart()
        )

        return self._add(content, raw)
