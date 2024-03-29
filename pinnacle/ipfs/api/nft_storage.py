from datetime import datetime

import httpx
from pydantic import BaseModel
from pydantic import Field

from ...constants.pin_services import NFT_STORAGE_SERVICE
from ..config import Config
from ..content import Content
from ..models import Pin
from ..models import PinMeta
from .pin_api import AsyncPinAPI
from .pin_api import PinAPI
from .pin_api import PinMixin


class NFT(BaseModel):
    cid: str
    size: float = Field(
        gt=0, default=132614, description="Size in bytes of the NFT data."
    )
    created: datetime | None = None
    type: str | None = Field(
        None,
        example="image/jpeg",
        description="MIME type of the uploaded file",
    )
    scope: str | None = Field(
        default="default",
        description="Name of the JWT token used to create this NFT.",
    )
    pin: Pin | None = None


class NFTStorageAdd(BaseModel):
    ok: bool
    value: NFT

    @property
    def cid(self):
        return self.value.cid


class NFTStorageMixin(PinMixin):
    global_config = Config(base_url=NFT_STORAGE_SERVICE)

    def _add(self, content: Content, raw_response: httpx.Response, *args, **kwds):
        response = super()._add(content, raw_response, NFTStorageAdd)

        nft = response.value

        return nft.pin or Pin(
            cid=response.cid,
            name=content.basename,
            meta=PinMeta.from_model(nft, exclude={"cid"}),
        )


class NFTStorage(NFTStorageMixin, PinAPI):
    def add(self, content: Content, *, cid_version: int = 1):
        raw = self._post("upload", **content._prepare())

        return self._add(content, raw)


class AsyncNFTStorage(NFTStorageMixin, AsyncPinAPI):
    async def add(self, content: Content, *, cid_version: int = 1):
        raw = await self._post("upload", **content._prepare())

        return self._add(content, raw)
