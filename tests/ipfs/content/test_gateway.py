import pytest

from pinnacle.ipfs.content import Gateway
from pinnacle.ipfs.content.content import UnsupportedSubdomainGateway

CID = "bafkreifjjcie6lypi6ny7amxnfftagclbuxndqonfipmb64f2km2devei4"

PATH_GATEWAY_HTTP = f"http://test/ipfs/{CID}/"
SUBDOMAIN_GATEWAY_HTTP = f"http://{CID}.ipfs.test/"

PATH_GATEWAY_HTTPS = f"https://test/ipfs/{CID}/"
SUBDOMAIN_GATEWAY_HTTPS = f"https://{CID}.ipfs.test/"


@pytest.fixture
def gateways():
    http_gw = Gateway("test", is_subdomain_supported=True)
    https_gw = Gateway("test", is_subdomain_supported=True, scheme="https")

    return http_gw, https_gw


def test_path_gateway(gateways):
    http_gateway, https_gateway = gateways

    assert http_gateway.path_gateway(CID) == PATH_GATEWAY_HTTP
    assert https_gateway.path_gateway(CID) == PATH_GATEWAY_HTTPS


def test_subdomain_gateway(gateways):
    http_gateway, https_gateway = gateways

    assert http_gateway.subdomain_gateway(CID) == SUBDOMAIN_GATEWAY_HTTP
    assert https_gateway.subdomain_gateway(CID) == SUBDOMAIN_GATEWAY_HTTPS


def test_subdomain_gateway_fail():
    gateway = Gateway("test")

    with pytest.raises(UnsupportedSubdomainGateway):
        gateway.subdomain_gateway(CID)


def test_gateway():
    gateway = Gateway("test", True)

    assert gateway.gateway(CID, "path") == PATH_GATEWAY_HTTP
    assert gateway.gateway(CID, "subdomain") == SUBDOMAIN_GATEWAY_HTTP


def test_gateway_fail():
    gateway = Gateway("test", True)

    with pytest.raises(ValueError) as error:
        gateway.gateway("none", CID)
