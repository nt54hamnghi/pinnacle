from pathlib import Path
from unittest import mock

import psutil
import pytest
import respx

from pinnacle.ipfs.api.local_pin import LocalPin
from pinnacle.ipfs.api.local_pin import LocalPinMixin
from pinnacle.ipfs.api.local_pin import NoIPFSDaemonError
from pinnacle.ipfs.content import Content
from tests.ipfs.api.conftest import CID
from tests.ipfs.api.conftest import ENDPOINT
from tests.ipfs.api.conftest import make_url


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
    mocked_local_pin_add,
    filename: str,
    path: Path,
):
    patched.return_value = True

    with LocalPin() as pin, Content(path) as content:
        url = make_url(pin, ENDPOINT)
        respx.post(url, params={"cid-version": 1}).mock(
            return_value=mocked_local_pin_add
        )

        res = pin.add(content, cid_version=1)

    assert res.Hash == CID
    assert res.Name == filename


def test_LocalPin_add_fail(path: Path):
    with LocalPin() as pin, Content(path) as content:
        with pytest.raises(NoIPFSDaemonError):
            pin.add(content)
