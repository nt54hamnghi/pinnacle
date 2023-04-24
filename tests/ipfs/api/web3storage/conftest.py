import httpx
import pytest

from pinnacle.ipfs.api.web3_storage import Web3StorageAdd
from tests.ipfs.api.conftest import CID


@pytest.fixture
def mocked_web3storage_add():
    json = Web3StorageAdd(cid=CID, carCid=CID).json()
    return httpx.Response(200, content=json)
