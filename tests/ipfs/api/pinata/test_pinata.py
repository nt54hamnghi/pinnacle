from pathlib import Path

import respx

from pinnacle.ipfs.api.pinata import Pinata
from pinnacle.ipfs.content.content import Content
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@respx.mock
def test_Pinata_add(mocked_pinata_add, path: Path):
    with Pinata() as pin, Content(path) as content:
        url = make_url(pin, "pinning/pinFileToIPFS")
        respx.post(url).mock(return_value=mocked_pinata_add)

        res = pin.add(content, cid_version=1)

    assert res.cid == CID
    assert res.isDuplicate is False
