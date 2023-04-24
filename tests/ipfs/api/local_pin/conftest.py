import httpx
import pytest

from pinnacle.ipfs.api.local_pin import LocalPinAdd
from tests.ipfs.api.conftest import CID


@pytest.fixture
def mocked_local_pin_add(filename):
    json = LocalPinAdd(Hash=CID, Name=filename, Size=311).json()
    return httpx.Response(200, content=json)
