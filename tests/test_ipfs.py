import pathlib

import httpx
import pytest

from pinnacle.config import IMG_DIR
from pinnacle.ipfs.configuration import Configuration
from pinnacle.ipfs.content import IPFS_GATEWAY, LOCAL_GATEWAY, Content
from pinnacle.ipfs.pin import pin
from pinnacle.ipfs.pinner import (
    LocalPin,
    NFTStorage,
    NoIPFSDaemon,
    Pin,
    Pinata,
    Web3Storage,
)


@pytest.fixture
def filename():
    breed = "SHIBA_INU"
    path = IMG_DIR / (breed.lower().replace("_", "-") + ".png")
    cid = "QmYx6GsYAKnNzZ9A6NvEKV9nf1VaDzJrqDR23Y8YSkebLU"
    return path, cid


def check_content(content: Content, cid):
    assert content.cid == cid
    assert content.pinned
    assert content.gateway() == IPFS_GATEWAY.format(cid=cid)
    assert content.gateway("local") == LOCAL_GATEWAY.format(cid=cid)


def test_get_filename(filename) -> str:
    path: pathlib.Path = filename[0]
    root = "/windows10/Users/hamng/Desktop/web3/nfts/freecodecamp/v2/img"
    assert path.as_posix() == root + "/shiba-inu.png"


def test_pinata_authenticate():
    url = "https://api.pinata.cloud/data/testAuthentication"
    config = Configuration(url, keyname="PINATA_KEY")
    resp = httpx.get(**config.setup())
    assert resp.status_code == 200


def test_no_ipfs_daemon():
    if LocalPin.ipfs_daemon_active():
        pytest.skip()

    with pytest.raises(NoIPFSDaemon):
        Configuration.from_pin(LocalPin())


def test_local_upload(filename):
    path, cid = filename
    content = pin(path, LocalPin())
    check_content(content, cid)


def test_dynamic_upload(filename):
    path, cid = filename
    url = "http://127.0.0.1:5001/api/v0/add"
    pinner = Pin(url, callback=lambda r: r.json()["Hash"])
    content = Pinata(path, pinner)
    check_content(content, cid)


def test_pinning_wiht_meta(filename):
    path, _ = filename
    meta = dict(params={"only-hash": 1, "cid-version": 1})
    content = pin(path, LocalPin(), meta=meta)

    assert (
        content.cid
        == "bafkreibfkec3ybuwxirrym2pkmn3nlrq6ng4a7zbyiegs26pw2pkl3ehxy"
    )


def test_pinata_upload(filename):
    path, cid = filename
    content = pin(path, Pinata())
    check_content(content, cid)


def test_nft_storage(filename):
    path, _ = filename
    # cid = "bafkreibfkec3ybuwxirrym2pkmn3nlrq6ng4a7zbyiegs26pw2pkl3ehxy"
    content = pin(path, NFTStorage())
    assert content.pinned

    print(content.cid)


def test_web3_storage(filename):
    path, _ = filename
    cid = "bafkreibfkec3ybuwxirrym2pkmn3nlrq6ng4a7zbyiegs26pw2pkl3ehxy"
    content = pin(path, Web3Storage())

    assert content.pinned
    assert content.cid == cid
