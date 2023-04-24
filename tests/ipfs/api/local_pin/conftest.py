import httpx
import pytest

from pinnacle.ipfs.api.local_pin import LocalPinAdd


@pytest.fixture
def cid_v1():
    return "bafkreifjjcie6lypi6ny7amxnfftagclbuxndqonfipmb64f2km2devei4"


@pytest.fixture
def mocked_add(filename, cid_v1):
    json = LocalPinAdd(Hash=cid_v1, Name=filename, Size=311).json()
    return httpx.Response(200, content=json)
