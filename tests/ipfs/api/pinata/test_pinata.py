from pathlib import Path

import respx

from pinnacle.ipfs.api.pinata import Pinata
from pinnacle.ipfs.content.content import Content
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import make_url


@respx.mock
def test_Pinata_add(mocked_pinata_add, filename: str, path: Path):
    with Pinata() as pin, Content(path) as content:
        url = make_url(pin, "pinning/pinFileToIPFS")
        respx.post(url).mock(return_value=mocked_pinata_add)

        res = pin.add(content, cid_version=1)

    assert isinstance(res, Pin)
    assert res.cid == CID
    assert res.name == filename
