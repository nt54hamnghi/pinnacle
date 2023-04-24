from datetime import datetime

import httpx
import pytest

from pinnacle.ipfs.api.pinata import PinataAdd
from tests.ipfs.api.conftest import CID


@pytest.fixture
def mocked_pinata_add():
    json = PinataAdd(
        IpfsHash=CID,
        PinSize=311,
        Timestamp=datetime.now(),
        isDuplicate=False,
    ).json()
    return httpx.Response(200, content=json)
