from io import UnsupportedOperation
from pathlib import Path

import pytest

from pinnacle.ipfs.content.content import AsyncContent


@pytest.fixture
def async_content(path):
    return AsyncContent(path)


@pytest.mark.anyio
async def test_async_content(async_content: AsyncContent):
    try:
        await async_content.open()
    except:  # pragma: no cover
        pass
    else:
        assert async_content.opened
        assert async_content._bytes is not None
    finally:
        await async_content.close()


@pytest.mark.anyio
async def test_async_content_context_manager(path: Path):
    async with AsyncContent(path) as content:
        assert content.opened
        assert content._bytes is not None

    assert content.closed


@pytest.mark.anyio
async def test_async_reopen_fail(path: Path):
    async with AsyncContent(path) as content:
        with pytest.raises(UnsupportedOperation):
            await content.open()


@pytest.mark.anyio
async def test_close_before_open(async_content: AsyncContent):
    with pytest.raises(UnsupportedOperation):
        await async_content.close()
