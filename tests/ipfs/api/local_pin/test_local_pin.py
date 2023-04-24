from pathlib import Path
from unittest import mock

import psutil
import pytest
import respx

from pinnacle.ipfs.api.local_pin import LocalPin
from pinnacle.ipfs.api.local_pin import LocalPinMixin
from pinnacle.ipfs.api.local_pin import NoIPFSDaemonError
from pinnacle.ipfs.api.pin_api import urljoin
from pinnacle.ipfs.content import Content

TEST_URL = "http://localhost"
ENDPOINT = "add"


def make_url(pin: LocalPin, endpoint: str):
    base = pin.config.url
    return urljoin(base, endpoint)


mock_ipfs = mock.MagicMock(spec=psutil.Process)
mock_ipfs.name.return_value = "ipfs"


@pytest.mark.parametrize(
    ("process", "expected"),
    (
        ([], False),
        ([mock_ipfs], True),
    ),
)
@mock.patch("pinnacle.ipfs.api.local_pin.psutil.process_iter")
def test_ipfs_daemon_active_true(patched, process, expected):
    patched.return_value = process

    assert LocalPinMixin.ipfs_daemon_active() is expected


@respx.mock
@mock.patch("pinnacle.ipfs.api.local_pin.LocalPinMixin.ipfs_daemon_active")
def test_LocalPin_add(
    patched,
    mocked_add,
    filename: str,
    path: Path,
    cid_v1: str,
):
    patched.return_value = True

    with LocalPin() as pin, Content(path) as content:
        url = make_url(pin, "add")
        respx.post(url, params={"cid-version": 1}).mock(return_value=mocked_add)

        print()
        print(pin.config.url)
        print(url)
        print(f"{pin.config.url}/{ENDPOINT}")

        res = pin.add(content, cid_version=1)

    assert res.Hash == cid_v1
    assert res.Name == filename


def test_LocalPin_add_fail(path: Path):
    with LocalPin() as pin, Content(path) as content:
        with pytest.raises(NoIPFSDaemonError):
            pin.add(content)
