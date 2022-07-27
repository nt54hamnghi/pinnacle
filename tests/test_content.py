import pytest

from pinnacle.config import IMG_DIR
from pinnacle.ipfs.content import IPFS_GATEWAY, LOCAL_GATEWAY, Content


@pytest.fixture
def path():
    filename = "shiba-inu.png"
    return IMG_DIR / filename, filename


def test_init(path):
    path, filename = path
    content = Content(path)
    print(content)
    assert content.basename == filename


def test_invalid_path():
    with pytest.raises(FileNotFoundError):
        Content(IMG_DIR / "shib.png")


def test_noninit_field(path):
    path, _ = path
    with pytest.raises(TypeError):
        Content(path, "application/json", True, "...")


def test_get_gateway(path):
    path, _ = path
    cid = "QmYx6GsYAKnNzZ9A6NvEKV9nf1VaDzJrqDR23Y8YSkebLU"
    content = Content(path)
    content.pinned = True
    content.cid = cid
    assert content.gateway() == IPFS_GATEWAY.format(cid=cid)
    assert content.gateway("local") == LOCAL_GATEWAY.format(cid=cid)


def test_fail_get_gateway(path):
    path, _ = path
    content = Content(path)
    content.cid = "testcid"

    # Not pinned
    with pytest.raises(ValueError):
        content.gateway()

    # invalid gataway category
    with pytest.raises(ValueError):
        content.gateway("custom")


def test_prepare(path):
    content = Content(path[0], "application/json")
    expected = dict(file=(path[1], content.read(), "application/json"))
    assert content.format() == expected
