from itertools import product
from pathlib import Path
from typing import Literal, TypeAlias
from unittest import mock

import pytest

from pinnacle.constants import IMG_DIR
from pinnacle.ipfs.content import Gateway
from pinnacle.ipfs.content.content import (
    GATEWAYS,
    GATEWAYS_STORE,
    SUBDOMAIN_SUPPORTED_GATEWAYS,
    BaseContent,
)

CID = "bafkreifjjcie6lypi6ny7amxnfftagclbuxndqonfipmb64f2km2devei4"

PATH_GATEWAY_HTTP = f"http://test/ipfs/{CID}/"
SUBDOMAIN_GATEWAY_HTTP = f"http://{CID}.ipfs.test/"

PATH_GATEWAY_HTTPS = f"https://test/ipfs/{CID}/"
SUBDOMAIN_GATEWAY_HTTPS = f"https://{CID}.ipfs.test/"

URI = f"ipfs://{CID}"


@pytest.fixture
def img_path():
    filename = "han.png"
    return IMG_DIR / filename, filename


ImgPathFixture: TypeAlias = tuple[Path, Literal["han.png"]]


@pytest.fixture
def base_content(img_path):
    path, _ = img_path
    return BaseContent(path)


def test_content_basename(
    base_content: BaseContent, img_path: ImgPathFixture
):
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
    base_content.set_pinned_status(CID)

    assert base_content.is_pinned is True
    assert base_content.cid == CID


def test_uri(base_content: BaseContent):
    base_content.set_pinned_status(CID)
    assert base_content.uri == URI


def test_uri_fail(base_content: BaseContent):
    with pytest.raises(ValueError) as error:
        assert base_content.uri == URI

    assert error.match("Content is not pinned yet")


def test_prepare(base_content: BaseContent):
    base_content._bytes = b""

    assert base_content._prepare() == dict(
        content=b"", headers={"Content-Type": base_content.mimetype}
    )


def test_prepare_fail(base_content: BaseContent):
    with pytest.raises(ValueError) as error:
        base_content._prepare()

    assert error.match("Content's bytes has not been read")


def test_prepare_multipart(base_content: BaseContent):
    base_content._bytes = b""

    assert base_content._prepare_multipart() == dict(
        files={"file": (base_content.basename, b"")}
    )
    assert base_content._prepare_multipart(include_mimetype=True) == dict(
        files={"file": (base_content.basename, b"", base_content.mimetype)}
    )


def test_prepare_multipart_fail(base_content: BaseContent):
    with pytest.raises(ValueError) as error:
        base_content._prepare_multipart()

    assert error.match("Content's bytes has not been read")


@pytest.mark.parametrize(
    ("gateway_name", "gateway_type"),
    product(GATEWAYS, ("path",)),
)
def test_get_gateway(gateway_name, gateway_type, base_content: BaseContent):
    base_content.set_pinned_status(CID)
    gw = base_content.get_gateway(name=gateway_name, type=gateway_type)

    assert gw == GATEWAYS_STORE[gateway_name].gateway(CID, gateway_type)


@pytest.mark.parametrize(
    ("gateway_name", "gateway_type"),
    product(SUBDOMAIN_SUPPORTED_GATEWAYS, ("path", "subdomain")),
)
def test_get_gateway_subdomain_supported(
    gateway_name, gateway_type, base_content: BaseContent
):
    base_content.set_pinned_status(CID)
    gw = base_content.get_gateway(name=gateway_name, type=gateway_type)

    assert gw == GATEWAYS_STORE[gateway_name].gateway(CID, gateway_type)


def test_content_add_gateway(base_content: BaseContent):
    test_gateway = Gateway("test", True, "https")
    base_content.add_gateway(test_gateway)
    base_content.set_pinned_status(CID)

    assert base_content.get_gateway(type="path") == PATH_GATEWAY_HTTPS
    assert (
        base_content.get_gateway(type="subdomain") == SUBDOMAIN_GATEWAY_HTTPS
    )


def test_get_gateway_fail(base_content: BaseContent):
    with pytest.raises(ValueError) as error:
        base_content.get_gateway()

    assert error.match("Content is not pinned yet")
