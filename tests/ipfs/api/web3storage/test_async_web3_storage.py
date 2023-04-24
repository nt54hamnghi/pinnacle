from pathlib import Path

import pytest
import respx

from pinnacle.ipfs.api.web3_storage import AsyncWeb3Storage
from pinnacle.ipfs.content.content import AsyncContent
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@pytest.mark.anyio
@respx.mock
async def test_AsyncWeb3Storage_add(mocked_web3storage_add, filename: str, path: Path):
    async with AsyncWeb3Storage() as pin, AsyncContent(path) as content:
        url = make_url(pin, "upload")
        respx.post(url).mock(return_value=mocked_web3storage_add)

        res = await pin.add(content, cid_version=1)

    assert isinstance(res, Pin)
    assert res.cid == CID
    assert res.name == filename
