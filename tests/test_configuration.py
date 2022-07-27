import pytest

from pinnacle.ipfs.configuration import (
    Authentication,
    AuthenticationKeyNotFound,
    Configuration,
    EnvironmentVariableNotFound,
    load_environment_config,
)


@pytest.fixture
def token():
    keyname = "TEST_KEY"
    return keyname, load_environment_config(keyname)


@pytest.fixture
def auth():
    key = "1c561c6ca273a2af80afd08db6b2a24b8782c2bcd79b69dbcab66de3574c9ccf"
    return key, f"Bearer {key}"


def test_load_environment_config(token, auth):
    assert token[1] == auth[0]


def test_fail_load_environment_config(token):
    # cannot load from system environment
    with pytest.raises(EnvironmentVariableNotFound):
        load_environment_config("TEST_TOKEN", "environment")

    # incorrect source
    with pytest.raises(ValueError):
        load_environment_config(token[0], "custom")

    # invalid keyname
    with pytest.raises(EnvironmentVariableNotFound):
        load_environment_config(token[1])


def test_init_Authentication(token, auth):
    authentication = Authentication(token[1])
    assert authentication.body == auth[1]


def test_from_env_Authentication(token, auth):
    authentication = Authentication.from_env(token[0])
    assert authentication.body == auth[1]


def test_fail_from_env_Authentication():
    with pytest.raises(AuthenticationKeyNotFound):
        Authentication.from_env("TEST")


def test_init_Configuration_no_auth():
    url = "http://127.0.0.1:5001/api/v0/add"
    cfg = Configuration(url)
    assert cfg.no_auth


def test_init_Configuration_with_token(token, auth):
    url = "http://127.0.0.1:5001/api/v0/add"
    cfg = Configuration(url, token=token[1])
    assert not cfg.no_auth
    assert cfg.auth.body == auth[1]


def test_init_Configuration_with_keyname(token, auth):
    url = "http://127.0.0.1:5001/api/v0/add"
    cfg = Configuration(url, keyname=token[0])
    assert not cfg.no_auth
    assert cfg.auth.body == auth[1]


def test_Configuration_params(token):
    url = "http://127.0.0.1:5001/api/v0/add"
    cfg = Configuration(
        url, keyname=token[0], meta=dict(params={"only-hash": 1})
    )
    print(cfg.setup())
