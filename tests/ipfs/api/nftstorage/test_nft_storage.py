from pathlib import Path

import respx

from pinnacle.ipfs.api.nft_storage import NFTStorage
from pinnacle.ipfs.content.content import Content
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@respx.mock
def test_NFTStorage_add(mocked_nftstorage_add, filename: str, path: Path):
    with NFTStorage() as pin, Content(path) as content:
        url = make_url(pin, "upload")
        respx.post(url).mock(return_value=mocked_nftstorage_add)

        res = pin.add(content, cid_version=1)

    assert isinstance(res, Pin)
    assert res.cid == CID
    assert res.name == filename
