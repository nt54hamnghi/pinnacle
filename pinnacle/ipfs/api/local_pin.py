from email import header
import httpx
from pydantic import BaseModel, Field

from pinnacle.ipfs.content.content import Content

from .pin_api import PinAPI


class NoIPFSDaemonError(Exception):
    ...


class LocalPinAddResponse(BaseModel):
    Name: str
    Hash: str
    Size: int = Field(gt=0)
    Bytes: int | None = None


class LocalPinAPI(PinAPI):
    def add(self, content: Content, cid_version: int = 1):
        try:
            raw = self._call_api(
                "POST",
                "add",
                files=content.prepare(),
                params={"cid-version": cid_version},
            )
            raw.raise_for_status()
        except httpx.ConnectError:
            raise NoIPFSDaemonError("IPFS daemon is not running")
        else:
            print(raw.request.headers)
            response = LocalPinAddResponse(**raw.json())
            pinned_cid = response.Hash
            content.pinned(pinned_cid)

            return response.dict()
