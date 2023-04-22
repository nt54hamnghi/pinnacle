from itertools import product

import httpx
import pytest
import respx

from pinnacle.ipfs import Config
from pinnacle.ipfs import Content
from pinnacle.ipfs.api import AsyncPinAPI


TEST_URL = "http://localhost"
ENDPOINT = "add"


def make_url(pin: AsyncPinAPI, endpoint: str):
    return f"{pin.config.url}/{endpoint}"


@pytest.fixture
def anyio_backend():
    return "asyncio"


class TestAsyncPinAPI(AsyncPinAPI):
    __test__ = False
    global_config = Config(url=TEST_URL)

    async def add(self, content: Content, *, cid_version: int = 1):
        ...  # pragma: no cover


@pytest.mark.parametrize(
    "api_client",
    (httpx.AsyncClient(), None),
    ids=["argument", "default"],
)
def test_init_AsyncPinAPI(api_client):
    pin = TestAsyncPinAPI(api_client=api_client)

    assert isinstance(pin.api_client, httpx.AsyncClient)


@pytest.mark.anyio
async def test_AsyncPinAPI_as_context_manager():
    async with TestAsyncPinAPI() as pin:
        assert isinstance(pin, TestAsyncPinAPI)

    assert pin.api_client.is_closed


@pytest.mark.parametrize(
    ("method", "status_code"),
    product(
        ("GET", "POST", "DELETE"),
        (300, 204),
    ),
)
@pytest.mark.anyio
@respx.mock
async def test_async__request(method, status_code, params, headers):
    json = {"message": f"{method}-{status_code}"}
    mocked_response = httpx.Response(status_code, json=json)

    async with TestAsyncPinAPI() as pin:
        route = respx.request(
            method,
            make_url(pin, ENDPOINT),
            params=params,
            headers=headers,
        )
        route.mock(return_value=mocked_response)

        response = await pin._request(
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
@pytest.mark.anyio
@respx.mock
async def test_async__request_fail(method, status_code):
    async with TestAsyncPinAPI() as pin:
        respx.request(method, make_url(pin, ENDPOINT)) % status_code

        with pytest.raises(httpx.HTTPStatusError):
            res = await pin._request(method, ENDPOINT)
            res.raise_for_status()


@pytest.mark.anyio
@respx.mock
async def test__post(content, data):
    async with TestAsyncPinAPI() as pin:
        respx.post(make_url(pin, ENDPOINT), content=content) % 204

        response = await pin._post(ENDPOINT, content=content, data=data)

    assert response.status_code == 204


@pytest.mark.anyio
@respx.mock
async def test__get(headers, params):
    mocked_response = httpx.Response(200, json={"response": headers | params})

    async with TestAsyncPinAPI() as pin:
        route = respx.get(make_url(pin, ENDPOINT), headers=headers, params=params)
        route.mock(return_value=mocked_response)

        response = await pin._get(ENDPOINT, query_params=params, headers=headers)

    assert response.status_code == 200
    assert response.json() == mocked_response.json()
