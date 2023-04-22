import json

import pytest


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
def files():
    return {"file": ("filename", "test".encode(), "*/*")}


@pytest.fixture
def data():
    return {"option": json.dumps({"cidVersion": 1})}
