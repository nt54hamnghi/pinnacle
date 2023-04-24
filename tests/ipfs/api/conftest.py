import json

import pytest

from pinnacle.ipfs.api.pin_api import BasePinAPI
from pinnacle.ipfs.api.pin_api import urljoin


@pytest.fixture
def headers():
    return {"Authorization": "Bearer JWT", "Content-Type": "image/png"}


@pytest.fixture
def params():
    return {"query": "test"}


@pytest.fixture
def content():
    return "test".encode()


@pytest.fixture
def data():
    return {"option": json.dumps({"cidVersion": 1})}


TEST_URL = "http://localhost"
ENDPOINT = "add"
CID = "bafkreifjjcie6lypi6ny7amxnfftagclbuxndqonfipmb64f2km2devei4"


def make_url(pin: BasePinAPI, endpoint: str):
    base = pin.config.url
    return urljoin(base, endpoint)
