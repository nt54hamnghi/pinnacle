from itertools import product

import httpx
import pytest
import respx

from pinnacle.ipfs import Config
from pinnacle.ipfs import Content
from pinnacle.ipfs.api import PinAPI
from tests.ipfs.api.conftest import ENDPOINT
from tests.ipfs.api.conftest import make_url
from tests.ipfs.api.conftest import TEST_URL


class TestPinAPI(PinAPI):
    __test__ = False
    global_config = Config(base_url=TEST_URL)

    def add(self, content: Content, *, cid_version: int = 1):
        ...  # pragma: no cover


@pytest.mark.parametrize(
    "api_client",
    (httpx.Client(), None),
    ids=["argument", "default"],
)
def test_init_PinAPI(api_client):
    pin = TestPinAPI(api_client=api_client)

    assert isinstance(pin.api_client, httpx.Client)


def test_PinAPI_as_context_manager():
    with TestPinAPI() as pin:
        assert isinstance(pin, TestPinAPI)

    assert pin.api_client.is_closed


@pytest.mark.parametrize(
    ("method", "status_code"),
    product(
        ("GET", "POST", "DELETE"),
        (300, 204),
    ),
)
@respx.mock
def test__request(method, status_code, params, headers):
    json = {"message": f"{method}-{status_code}"}
    mocked_response = httpx.Response(status_code=status_code, json=json)

    with TestPinAPI() as pin:
        route = respx.request(
            method,
            make_url(pin, ENDPOINT),
            params=params,
            headers=headers,
        )
        route.mock(return_value=mocked_response)

        response = pin._request(
            method,
            ENDPOINT,
            query_params=params,
            headers=headers,
        )

    assert response.status_code == status_code
    assert response.json() == json


@pytest.mark.parametrize(
    ("method", "status_code"),
    product(("GET", "POST", "DELETE"), (404, 500)),
)
@respx.mock
def test__request_fail(method, status_code):
    with TestPinAPI() as pin:
        respx.request(method, make_url(pin, ENDPOINT)) % status_code

        with pytest.raises(httpx.HTTPStatusError):
            pin._request(method, ENDPOINT).raise_for_status()


@respx.mock
def test__post(content, data):
    with TestPinAPI() as pin:
        respx.post(make_url(pin, ENDPOINT), content=content) % 204

        response = pin._post(ENDPOINT, content=content, data=data)

    assert response.status_code == 204


@respx.mock
def test__get(headers, params):
    mocked_response = httpx.Response(200, json={"response": headers | params})

    with TestPinAPI() as pin:
        route = respx.get(make_url(pin, ENDPOINT), headers=headers, params=params)
        route.mock(return_value=mocked_response)

        response = pin._get(ENDPOINT, query_params=params, headers=headers)

    assert response.status_code == 200
    assert response.json() == mocked_response.json()
