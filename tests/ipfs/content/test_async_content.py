from io import UnsupportedOperation
from pathlib import Path
from typing import Literal, TypeAlias

import pytest

from pinnacle.constants import IMG_DIR
from pinnacle.ipfs.content.content import AsyncContent


@pytest.fixture
def img_path():
    filename = "han.png"
    return IMG_DIR / filename, filename


ImgPathFixture: TypeAlias = tuple[Path, Literal["han.png"]]


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def async_content(img_path):
    path, _ = img_path
    return AsyncContent(path)


@pytest.mark.anyio
async def test_async_content(async_content: AsyncContent):
    try:
        await async_content.open()
    except:
        pass
    else:
        assert async_content.opened
        assert async_content._bytes is not None
    finally:
        await async_content.close()


@pytest.mark.anyio
async def test_async_content_context_manager(img_path: ImgPathFixture):
    path, _ = img_path

    async with AsyncContent(path) as content:
        assert content.opened
        assert content._bytes is not None

    assert content.closed


@pytest.mark.anyio
async def test_async_reopen_fail(img_path: ImgPathFixture):
    path, _ = img_path

    async with AsyncContent(path) as content:
        with pytest.raises(UnsupportedOperation):
            await content.open()


@pytest.mark.anyio
async def test_close_before_open(async_content: AsyncContent):
    with pytest.raises(UnsupportedOperation):
        await async_content.close()
