from pathlib import Path

import pytest
import respx

from pinnacle.ipfs.api.pinata import AsyncPinata
from pinnacle.ipfs.content.content import AsyncContent
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@pytest.mark.anyio
@respx.mock
async def test_AsyncPinata_add(mocked_pinata_add, filename: str, path: Path):
    async with AsyncPinata() as pin, AsyncContent(path) as content:
        url = make_url(pin, "pinning/pinFileToIPFS")
        respx.post(url).mock(return_value=mocked_pinata_add)

        res = await pin.add(content, cid_version=1)

    assert isinstance(res, Pin)
    assert res.cid == CID
    assert res.name == filename
