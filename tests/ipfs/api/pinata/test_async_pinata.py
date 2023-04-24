from pathlib import Path

import pytest
import respx

from pinnacle.ipfs.api.pinata import AsyncPinata
from pinnacle.ipfs.content.content import AsyncContent
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@pytest.mark.anyio
@respx.mock
async def test_AsyncPinata_add(mocked_pinata_add, path: Path):
    async with AsyncPinata() as pin, AsyncContent(path) as content:
        url = make_url(pin, "pinning/pinFileToIPFS")
        respx.post(url).mock(return_value=mocked_pinata_add)

        res = await pin.add(content, cid_version=1)

    assert res.cid == CID
    assert res.isDuplicate is False
