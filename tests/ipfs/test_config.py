from unittest import mock

import pytest
from httpx import Request

from pinnacle.ipfs.config import _from_dot_env
from pinnacle.ipfs.config import _from_os_env
from pinnacle.ipfs.config import AuthKeyNotFoundError
from pinnacle.ipfs.config import BearerAuth
from pinnacle.ipfs.config import Config
from pinnacle.ipfs.config import ENVNotFoundError
from pinnacle.ipfs.config import MalformedURLError
from pinnacle.ipfs.config import sanitize_url

TEST_JWT = "d8a29446d9418907d51b9f146bdd0e8456e7d0cbe09cba0238df003a69f13289"
TEST_SERVICE = "http://localhost"
BEARER = f"Bearer {TEST_JWT}"


@mock.patch("pinnacle.ipfs.config.os.getenv", return_value=TEST_JWT)
def test_from_OS_env(mock_getenv):
    assert _from_os_env("TEST_JWT") == TEST_JWT


def test_from_OS_env_fail():
    with pytest.raises(ENVNotFoundError):
        _from_os_env("TEST_JWT")


@mock.patch(
    "pinnacle.ipfs.config.dotenv_values",
    return_value=dict(TEST_JWT=TEST_JWT),
)
def test_from_DOT_env(mock_dotenv):
    assert _from_dot_env("TEST_JWT") == TEST_JWT


def test_from_DOT_env_fail():
    with pytest.raises(ENVNotFoundError):
        _from_dot_env("TEST_JWT")


def test_init_Bearer():
    assert BearerAuth(TEST_JWT).bearer_token == BEARER


@mock.patch("pinnacle.ipfs.config.os.getenv", return_value=TEST_JWT)
def test_Bearer_from_env_OS_branch(auth):
    auth = BearerAuth.from_env("TEST_JWT")
    assert auth.bearer_token == BEARER


@mock.patch(
    "pinnacle.ipfs.config.dotenv_values",
    return_value=dict(TEST_JWT=TEST_JWT),
)
def test_Bearer_from_env_DOT_branch(auth):
    auth = BearerAuth.from_env("TEST_JWT")
    assert auth.bearer_token == BEARER


def test_Bearer_from_env_fail():
    with pytest.raises(AuthKeyNotFoundError):
        BearerAuth.from_env("TEST_JWT")


def test_auth_flow():
    auth = BearerAuth(TEST_JWT)
    flow = auth.auth_flow(Request("GET", TEST_SERVICE))
    request = next(flow)

    assert request.headers["Authorization"] == BEARER


def test_auth_flow_no_token():
    auth = BearerAuth()
    flow = auth.auth_flow(Request("GET", TEST_SERVICE))
    request = next(flow)

    with pytest.raises(KeyError):
        assert request.headers["Authorization"] == BEARER


@pytest.mark.parametrize(
    ("url", "expected"),
    (
        (
            "http://127.0.0.1:5001/api/v0?query=what#fragment",
            "http://127.0.0.1:5001/api/v0",
        ),
        (
            "https://api.pinata.cloud?query=what#fragment",
            "https://api.pinata.cloud",
        ),
        (
            "https://api.nft.storage?query=what#fragment",
            "https://api.nft.storage",
        ),
        (
            "https://api.web3.storage?query=what#fragment",
            "https://api.web3.storage",
        ),
    ),
    ids=["local-ip", "pinata", "nftstorage", "web3storage"],
)
def test_sanitize_url(url, expected):
    assert sanitize_url(url) == expected


@pytest.mark.parametrize(
    "url",
    (
        "http:/127.0.0.1:5001/api/v0",
        "https://api,pinata,cloud",
        "https;//api.nft.storage",
        "htts://api.web3.storage",
    ),
)
def test_sanitize_url_fail(url):
    with pytest.raises(MalformedURLError):
        sanitize_url(url)


@pytest.fixture
def config():
    return Config(TEST_SERVICE)


@pytest.fixture
def authless_config():
    return Config(TEST_SERVICE, authless=True)


def test_init_Config(authless_config: Config):
    assert authless_config.authless
    assert authless_config.auth is None
    assert authless_config.extra_params == {}


def test_update_params(config: Config):
    params = {"headers": {"Authorization": BEARER}}
    config.update_params(params)

    assert config.extra_params == params


def test_update_authentication(config: Config):
    auth = BearerAuth(TEST_JWT)
    config.update_authentication(auth)

    assert config.auth.bearer_token == BEARER


def test_update_authentication_fail(authless_config: Config):
    auth = BearerAuth(TEST_JWT)

    with pytest.raises(ValueError) as error:
        authless_config.update_authentication(auth)

    assert error.match("Cannot update authentication with an auth-less configuration")


def test_setup_without_auth(config: Config):
    assert config.setup() == {}


def test_setup_with_auth(config: Config):
    auth = BearerAuth(TEST_JWT)
    config.update_authentication(auth)

    assert config.setup() == dict(auth=auth)
