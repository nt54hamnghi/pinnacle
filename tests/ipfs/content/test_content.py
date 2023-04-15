import pytest

# from pinnacle.constants import IMG_DIR
from pinnacle.ipfs.content import Gateway
from pinnacle.ipfs.content.content import UnsupportedSubdomainGateway


CID = "bafkreifjjcie6lypi6ny7amxnfftagclbuxndqonfipmb64f2km2devei4"


@pytest.fixture
def gateways():
    http_gw = Gateway("test", is_subdomain_supported=True)
    https_gw = Gateway("test", is_subdomain_supported=True, scheme="https")

    return http_gw, https_gw


def test_create_gateway():
    gateway = Gateway("test")

    assert gateway.is_subdomain_supported is False
    assert gateway.scheme == "http"


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
