from datetime import datetime

import httpx
import pytest

from pinnacle.ipfs.api.nft_storage import NFT
from pinnacle.ipfs.api.nft_storage import NFTStorageAdd
from pinnacle.ipfs.models.models import Pin
from tests.ipfs.api.conftest import CID


@pytest.fixture
def mocked_nftstorage_add(filename):
    pin = Pin(cid=CID, name=filename)
    nft = NFT(cid=CID, created=datetime.now(), type="image/jpeg", pin=pin)
    json = NFTStorageAdd(ok=True, value=nft).json()

    return httpx.Response(200, content=json)
