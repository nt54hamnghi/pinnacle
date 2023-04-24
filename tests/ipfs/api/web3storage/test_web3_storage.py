from pathlib import Path

import respx

from pinnacle.ipfs.api.web3_storage import Web3Storage
from pinnacle.ipfs.content.content import Content
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@respx.mock
def test_Web3Storage_add(mocked_web3storage_add, filename: str, path: Path):
    with Web3Storage() as pin, Content(path) as content:
        url = make_url(pin, "upload")
        respx.post(url).mock(return_value=mocked_web3storage_add)

        res = pin.add(content, cid_version=1)

    assert isinstance(res, Pin)
    assert res.cid == CID
    assert res.name == filename
