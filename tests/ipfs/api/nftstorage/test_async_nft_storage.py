from pathlib import Path

import pytest
import respx

from pinnacle.ipfs.api.nft_storage import AsyncNFTStorage
from pinnacle.ipfs.content.content import AsyncContent
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@pytest.mark.anyio
@respx.mock
async def test_AsyncNFTStorage_add(mocked_nftstorage_add, filename: str, path: Path):
    async with AsyncNFTStorage() as pin, AsyncContent(path) as content:
        url = make_url(pin, "upload")
        respx.post(url).mock(return_value=mocked_nftstorage_add)

        res = await pin.add(content, cid_version=1)

    assert isinstance(res, Pin)
    assert res.cid == CID
    assert res.name == filename
