from datetime import datetime
from typing import ClassVar
from unittest.mock import MagicMock

import httpx
import pytest
import respx
from pydantic import BaseModel
from pydantic import Field
from pydantic import parse_obj_as

from pinnacle.ipfs.api import PinAPI
from pinnacle.ipfs.api import PinMixin
from pinnacle.ipfs.config import Config
from pinnacle.ipfs.content import Content

TEST_URL = "http://localhost/add"
TEST_CID = "bafkreigd2qu62erpk32kt3jh5ogxfzhyjyoyx3mnvblxurx2kwuhi2aadu"


class TestResponseModel(BaseModel):
    # annotate as ClassVar to prevent pydantic from creating the field as attribute
    __test__: ClassVar[bool] = False

    cid: str
    date: datetime = Field(default_factory=datetime.now)


TEST_RESPONSE = TestResponseModel(cid=TEST_CID)


@pytest.mark.parametrize(
    "mocked",
    (
        httpx.Response(200, json=TEST_RESPONSE.json()),
        httpx.Response(200, content=TEST_RESPONSE.json()),
    ),
    ids=["str_response", "dict_response"],
)
@respx.mock
def test_transfrom_response(mocked: httpx.Response):
    respx.get(TEST_URL).mock(return_value=mocked)
    raw = httpx.get(TEST_URL)
    response = PinMixin.transform_response(raw, TestResponseModel)

    assert isinstance(response, TestResponseModel)


@pytest.fixture
def mocked_content():
    mock = MagicMock(spec=Content, is_pinned=True, cid=None)

    def _(cid):
        mock.cid = cid
        mock.is_pinned = True

    mock.set_pinned_status.side_effect = _

    return mock


@respx.mock
def test__add(mocked_content: Content):
    mocked_response = httpx.Response(200, content=TEST_RESPONSE.json())
    respx.get(TEST_URL).mock(return_value=mocked_response)
    raw = httpx.get(TEST_URL)

    PinMixin()._add(mocked_content, raw, TestResponseModel)

    assert mocked_content.is_pinned
    assert mocked_content.cid == TEST_RESPONSE.cid
