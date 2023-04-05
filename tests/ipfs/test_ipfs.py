import httpx
import pytest

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.config import BearerAuth, Config
from pinnacle.ipfs.content import IPFS_GATEWAY, LOCAL_GATEWAY, Content
from pinnacle.ipfs.api.pin import pin
from pinnacle.ipfs.api.pin_client import (
    Local,
    NFTStorage,
    NoIPFSDaemon,
    PinClient,
    Pinata,
    Web3Storage,
    ipfs_daemon_active,
)


@pytest.fixture
def filename():
    v0 = "QmVZrwrWQo9Yk9Xx4PpMWzbXoCCeD6ArFVp6berEH5Fzmh"
    v1 = "bafkreih4wi2g7hyznblnwzs4wggznkdn46xm6hwjfsbnim7n4kymvkfrkm"
    path = IMG_DIR / "rin.png"
    return path, (v0, v1)


def check_content(content: Content, cid):
    assert content.cid == cid
    assert content.pinned
    assert content.gateway() == IPFS_GATEWAY.format(cid=cid)
    assert content.gateway("local") == LOCAL_GATEWAY.format(cid=cid)


def test_pinata_authenticate():
    url = "https://api.pinata.cloud/data/testAuthentication"
    auth = BearerAuth.from_env("PINATA_KEY")
    resp = httpx.get(url, headers={"Authorization": auth.bearer_token})
    assert resp.status_code == 200


def test_no_ipfs_daemon():
    if ipfs_daemon_active():
        pytest.skip()

    with pytest.raises(NoIPFSDaemon):
        Config(Local())


def test_local(filename):
    path, (cid, _) = filename
    content = pin(path, Local())
    check_content(content, cid)


def test_pin_with_extra_params(filename):
    path, (_, cid) = filename
    extra = dict(params={"only-hash": 1, "cid-version": 1})
    content = pin(path, Local(), extra=extra)

    assert content.cid == cid


def test_dynamic(filename):
    path, (cid, _) = filename
    url = "http://127.0.0.1:5001/api/v0/add"

    pinner = PinClient(url, getter=lambda r: r.json()["Hash"])
    content = pin(path, pinner)
    check_content(content, cid)


def test_pinata(filename):
    path, (cid, _) = filename
    content = pin(path, Pinata())
    check_content(content, cid)


def test_nft_storage(filename):
    path, _ = filename
    content = pin(path, NFTStorage())
    raw = "bafybeid3n6a432eh6lqdl6igddmajn5qrtdaqqrbvjhuzxrlpx7syqasku"
    print(content.cid)

    assert content.pinned
    assert content.cid == raw


def test_web3_storage(filename):
    path, (_, cid) = filename
    content = pin(path, Web3Storage())

    assert content.pinned
    assert content.cid == cid
