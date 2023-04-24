from pathlib import Path
from unittest import mock

import pytest
import respx

from pinnacle.ipfs.api.local_pin import AsyncLocalPin
from pinnacle.ipfs.api.local_pin import NoIPFSDaemonError
from pinnacle.ipfs.content import AsyncContent
from tests.ipfs.api.conftest import ENDPOINT
from tests.ipfs.api.conftest import make_url


@pytest.mark.anyio
@respx.mock
@mock.patch("pinnacle.ipfs.api.local_pin.LocalPinMixin.ipfs_daemon_active")
async def test_LocalPin_add(
    patched,
    mocked_add,
    filename: str,
    path: Path,
    cid_v1: str,
):
    patched.return_value = True

    async with AsyncLocalPin() as pin, AsyncContent(path) as content:
        url = make_url(pin, ENDPOINT)
        respx.post(url, params={"cid-version": 1}).mock(return_value=mocked_add)

        res = await pin.add(content, cid_version=1)

    assert res.Hash == cid_v1
    assert res.Name == filename


@pytest.mark.anyio
async def test_LocalPin_add_fail(path: Path):
    async with AsyncLocalPin() as pin, AsyncContent(path) as content:
        with pytest.raises(NoIPFSDaemonError):
            await pin.add(content)
