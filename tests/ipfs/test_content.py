import pytest

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.content.content import IPFS_GATEWAY, LOCAL_GATEWAY, Content


@pytest.fixture
def path():
    filename = "han.png"
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
    cid = "QmRWKJ42WTLe4ovwwpX9gMepbaRcpjsNNLsMcqs6Cqa27X"

    content = Content(path)
    content.is_pinned = True
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
    assert content.prepare() == expected
