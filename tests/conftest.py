import pytest

from pinnacle.constants.dirs import IMG_DIR


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def filename():
    return "han.png"


@pytest.fixture
def path(filename: str):
    return IMG_DIR / filename
