from unittest import mock

import pytest

from pinnacle.ipfs import Config
from pinnacle.ipfs.api.pin_api import BasePinAPI
from pinnacle.ipfs.api.pin_api import MissingConfigurationError
from pinnacle.ipfs.api.pin_api import urljoin
from tests.ipfs.api.conftest import ENDPOINT
from tests.ipfs.api.conftest import TEST_URL

TEST_JWT = "d8a29446d9418907d51b9f146bdd0e8456e7d0cbe09cba0238df003a69f13289"
BEARER = f"Bearer {TEST_JWT}"
EXTRA_PARAMS = {"headers": {"Content-Type": "*/*"}}


class TestBasePinAPI(BasePinAPI):
    __test__ = False
    global_config = Config(base_url=TEST_URL, extra_params=EXTRA_PARAMS)


@pytest.mark.parametrize(
    ("base, endpoint, expected"),
    (
        ("https://example.com", "endpoint", "https://example.com/endpoint"),
        ("https://example.com/", "endpoint", "https://example.com/endpoint"),
        ("https://example.com", "/endpoint", "https://example.com/endpoint"),
        ("https://example.com/", "/endpoint", "https://example.com/endpoint"),
    ),
    ids=["without", "trailing", "leading", "both"],
)
def test_urljoin(base, endpoint, expected):
    assert urljoin(base, endpoint) == expected


@pytest.fixture
def default_pin():
    return TestBasePinAPI()


def test_init_BasePinAPI_with_defaults(default_pin: TestBasePinAPI):
    assert not default_pin.authless
    assert default_pin.config.url == TEST_URL
    assert default_pin.config.extra_params == EXTRA_PARAMS


def test_init_BasePinAPI():
    config = Config(TEST_URL)
    pin = TestBasePinAPI(config)

    assert pin.config.url == TEST_URL
    assert pin.config.extra_params == {}


def test_missing_config():
    class InvalidBasePin(BasePinAPI):
        ...

    with pytest.raises(MissingConfigurationError):
        InvalidBasePin()


def test_build_request_params():
    config = Config(TEST_URL)
    pin = TestBasePinAPI(config)

    request = pin._build_request_params(ENDPOINT)

    assert request == {
        "url": f"{TEST_URL}/{ENDPOINT}",
        "params": None,
        "headers": None,
    }


def test_build_request_params_with_args():
    config = Config(TEST_URL)
    pin = TestBasePinAPI(config)

    request = pin._build_request_params(
        ENDPOINT, query_params={"test": None}, headers={"content_type": None}
    )

    assert request == {
        "url": f"{TEST_URL}/{ENDPOINT}",
        "params": {"test": None},
        "headers": {"content_type": None},
    }


def test_build_request_params_fail():
    config = Config(TEST_URL)
    pin = TestBasePinAPI(config)

    with pytest.raises(ValueError) as error:
        pin._build_request_params("")

    assert error.match("Endpoint cannot be empty")


def test_authenticate_with_TOKEN(default_pin: TestBasePinAPI):
    default_pin.authenticate_with_token(TEST_JWT)

    assert default_pin.config.auth.bearer_token == BEARER


@mock.patch("pinnacle.ipfs.config.os.getenv", return_value=TEST_JWT)
def test_authenticate_with_ENV(mock_env, default_pin: TestBasePinAPI):
    default_pin.authenticate_with_env("TEST_JWT")

    assert default_pin.config.auth.bearer_token == BEARER
