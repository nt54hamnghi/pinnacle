import json
from datetime import datetime

import httpx
from pydantic import BaseModel, Field

from ...consts import PINATA_SERVICE
from ..config import BearerAuth, Config
from ..content import Content
from .pin_api import AsyncPinAPI, PinAPI, transform_response


class PinataAddResponse(BaseModel):
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


class PinantaMixin:
    global_config = Config(
        url=PINATA_SERVICE,
        auth=BearerAuth.from_env("PINATA_JWT"),
    )

    @staticmethod
    def _add(content: Content, raw_response: httpx.Response):
        response = transform_response(raw_response, PinataAddResponse)
        content.pinned(response.cid)

        return response


class Pinata(PinantaMixin, PinAPI):
    def add(self, content: Content, *, cid_version: int = 1):
        payload = {"pinataOptions": json.dumps({"cidVersion": cid_version})}
        raw = self._post(
            "pinning/pinFileToIPFS", files=content.prepare(), data=payload
        )

        return self._add(content, raw)


class AsyncPinata(PinantaMixin, AsyncPinAPI):
    async def add(self, content: Content, *, cid_version: int = 1):
        payload = {"pinataOptions": json.dumps({"cidVersion": cid_version})}
        raw = await self._post(
            "pinning/pinFileToIPFS", files=content.prepare(), data=payload
        )

        return self._add(content, raw)
