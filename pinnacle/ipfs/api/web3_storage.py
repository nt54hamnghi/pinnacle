import httpx
from pydantic import BaseModel

from ...constants.pin_services import WEB3_STORAGE_SERVICE
from ..config import Config
from ..content import Content
from .pin_api import AsyncPinAPI
from .pin_api import PinAPI
from .pin_api import PinMixin


class Web3StorageAdd(BaseModel):
    cid: str
    carCid: str


class Web3StorageMixin(PinMixin):
    global_config = Config(url=WEB3_STORAGE_SERVICE)

    def _add(self, content: Content, raw_response: httpx.Response, *args, **kwds):
        return super()._add(content, raw_response, Web3StorageAdd)


class Web3Storage(Web3StorageMixin, PinAPI):
    def add(self, content: Content, *, cid_version: int = 1):
        raw = self._post("upload", **content._prepare_multipart())

        return self._add(content, raw)


class AsyncWeb3Storage(Web3StorageMixin, AsyncPinAPI):
    async def add(self, content: Content, *, cid_version: int = 1):
        raw = await self._post("upload", **content._prepare_multipart())

        return self._add(content, raw)
