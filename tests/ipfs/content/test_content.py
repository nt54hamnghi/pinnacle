from unittest import mock
import pytest

from pinnacle.constants import IMG_DIR
from pinnacle.ipfs.content import Gateway
from pinnacle.ipfs.content.content import (
    UnsupportedSubdomainGateway,
    BaseContent,
)


CID = "bafkreifjjcie6lypi6ny7amxnfftagclbuxndqonfipmb64f2km2devei4"


@pytest.fixture
def gateways():
    http_gw = Gateway("test", is_subdomain_supported=True)
    https_gw = Gateway("test", is_subdomain_supported=True, scheme="https")

    return http_gw, https_gw


def test_path_gateway(gateways):
    http_gateway, https_gateway = gateways

    assert http_gateway.path_gateway(CID) == f"http://test/ipfs/{CID}/"
    assert https_gateway.path_gateway(CID) == f"https://test/ipfs/{CID}/"


def test_subdomain_gateway(gateways):
    http_gateway, https_gateway = gateways

    assert http_gateway.subdomain_gateway(CID) == f"http://{CID}.ipfs.test/"
    assert https_gateway.subdomain_gateway(CID) == f"https://{CID}.ipfs.test/"


def test_subdomain_gateway_fail():
    gateway = Gateway("test")

    with pytest.raises(UnsupportedSubdomainGateway):
        gateway.subdomain_gateway(CID)


def test_gateway():
    gateway = Gateway("test", True)

    assert gateway.gateway(CID, "path") == f"http://test/ipfs/{CID}/"
    assert gateway.gateway(CID, "subdomain") == f"http://{CID}.ipfs.test/"


def test_gateway_fail():
    gateway = Gateway("test", True)

    with pytest.raises(ValueError):
        gateway.gateway("none", CID)


@pytest.fixture
def img_path():
    filename = "han.png"
    return IMG_DIR / filename, filename


@pytest.fixture
def base_content(img_path):
    path, filename = img_path
    return BaseContent(path)


def test_content_basename(base_content, img_path):
    filename = img_path[1]
    assert base_content.basename == filename


def test_default_mimetype(base_content: BaseContent):
    assert base_content._mimetype == "application/octet-stream"
    assert base_content.mimetype == "image/png"


@mock.patch(
    "pinnacle.ipfs.content.content.mimetypes.guess_type",
    return_value=[None, None],
)
def test_cannot_guess_mimetype(mock_guess_type, base_content: BaseContent):
    assert base_content.mimetype == "application/octet-stream"


def test_set_mimetype(base_content: BaseContent):
    base_content.mimetype = "application/json"
    assert base_content.mimetype == "application/json"


def test_pinned(base_content: BaseContent):
    base_content.pinned(CID)

    assert base_content.is_pinned is True
    assert base_content.cid == CID


def test_uri(base_content: BaseContent):
    base_content.pinned(CID)
    assert base_content.uri == f"ipfs://{CID}"


def test_uri_fail(base_content: BaseContent):
    with pytest.raises(ValueError):
        assert base_content.uri == f"ipfs://{CID}"


def test_prepare(base_content: BaseContent):
    base_content._bytes = b""

    assert base_content._prepare() == dict(
        content=b"", headers={"Content-Type": base_content.mimetype}
    )


def test_prepare_fail(base_content: BaseContent):
    with pytest.raises(ValueError):
        base_content._prepare()
