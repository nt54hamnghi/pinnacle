from pathlib import Path

import pytest

from pinnacle.constants.dirs import IMG_DIR
from pinnacle.ipfs.content.content import Content


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def filename():
    return "han.png"


@pytest.fixture
def path(filename: str):
    return IMG_DIR / filename


@pytest.fixture
def content(path: Path):
    return Content(path)
