from unittest import mock

import pytest

from pinnacle.ipfs import Config
from pinnacle.ipfs.api.pin_api import BasePinAPI

TEST_JWT = "d8a29446d9418907d51b9f146bdd0e8456e7d0cbe09cba0238df003a69f13289"
TEST_SERVICE = "http://localhost"
BEARER = f"Bearer {TEST_JWT}"
EXTRA_PARAMS = {"headers": {"Content-Type": "*/*"}}


class TestPinAPI(BasePinAPI):
    __test__ = False
    global_config = Config(url=TEST_SERVICE, extra_params=EXTRA_PARAMS)


@pytest.fixture
def default_pin():
    return TestPinAPI()


def test_init_BasePinAPI_with_defaults(default_pin: TestPinAPI):
    assert not default_pin.authless
    assert default_pin.config.url == TEST_SERVICE
    assert default_pin.config.extra_params == EXTRA_PARAMS


def test_init_BasePinAPI():
    config = Config(TEST_SERVICE)
    pin = TestPinAPI(config)

    assert pin.config.url == TEST_SERVICE
    assert pin.config.extra_params == {}


def test_build_request_params():
    config = Config(TEST_SERVICE)
    pin = TestPinAPI(config)

    endpoint = "add"
    request = pin._build_request_params(endpoint)

    assert request == {
        "url": f"{TEST_SERVICE}/{endpoint}",
        "params": None,
        "headers": None,
    }


def test_build_request_params_with_args():
    config = Config(TEST_SERVICE)
    pin = TestPinAPI(config)

    endpoint = "add"
    request = pin._build_request_params(
        endpoint, query_params={"test": None}, headers={"content_type": None}
    )

    assert request == {
        "url": f"{TEST_SERVICE}/{endpoint}",
        "params": {"test": None},
        "headers": {"content_type": None},
    }


def test_authenticate_with_TOKEN(default_pin: TestPinAPI):
    default_pin.authenticate_with_token(TEST_JWT)

    assert default_pin.config.auth.bearer_token == BEARER


@mock.patch("pinnacle.ipfs.config.os.getenv", return_value=TEST_JWT)
def test_authenticate_with_ENV(mock_env, default_pin: TestPinAPI):
    default_pin.authenticate_with_env("TEST_JWT")

    assert default_pin.config.auth.bearer_token == BEARER
