import pytest

from pinnacle.ipfs.config import (
    BearerAuth,
    AuthKeyNotFound,
    Config,
    ENVNotFound,
    _from_dot_env,
    _from_os_env,
)
from pinnacle.ipfs.api.pin_api import Local


@pytest.fixture
def auth():
    raw = "1c561c6ca273a2af80afd08db6b2a24b8782c2bcd79b69dbcab66de3574c9ccf"
    keyname = "TEST_KEY"
    key = _from_dot_env(keyname)
    bearer = f"Bearer {key}"

    assert key == raw

    return keyname, key, bearer


def test_from_os_env(auth):
    with pytest.raises(ENVNotFound):
        _from_os_env("RANDOM")
    assert _from_os_env("SHELL") == "/bin/bash"


def test_from_dot_env(auth):
    keyname, *_ = auth
    raw = "1c561c6ca273a2af80afd08db6b2a24b8782c2bcd79b69dbcab66de3574c9ccf"

    with pytest.raises(ENVNotFound):
        _from_dot_env("RANDOM")

    assert _from_dot_env(keyname) == raw


def test_init_Authentication(auth):
    _, token, bearer = auth
    authen = BearerAuth(token)
    assert authen.bearer_token == bearer


def test_from_env_Authentication(auth):
    keyname, _, bearer = auth
    authen = BearerAuth.from_env(keyname)
    assert authen.bearer_token == bearer


def test_fail_from_env_Authentication():
    # invalid keyname
    with pytest.raises(AuthKeyNotFound):
        BearerAuth.from_env("INVALID")


def test_no_auth_Configuration():
    local = Local()
    cfg = Config(local)
    assert cfg.no_authentication


def test_pass_auth_Configuration(auth):
    keyname, *_ = auth
    auth = BearerAuth.from_env(keyname)
    cfg = Config(Local(), auth)
    assert not cfg.no_authentication
