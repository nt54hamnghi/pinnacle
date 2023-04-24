from pathlib import Path

import pytest
import respx

from pinnacle.ipfs.api.nft_storage import AsyncNFTStorage
from pinnacle.ipfs.content.content import AsyncContent
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@pytest.mark.anyio
@respx.mock
async def test_AsyncNFTStorage_add(mocked_nftstorage_add, path: Path):
    async with AsyncNFTStorage() as pin, AsyncContent(path) as content:
        url = make_url(pin, "upload")
        respx.post(url).mock(return_value=mocked_nftstorage_add)

        res = await pin.add(content, cid_version=1)

    assert res.ok
    assert res.value.cid == CID
    assert res.value.pin.cid == CID
