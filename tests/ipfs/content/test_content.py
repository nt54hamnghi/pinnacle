from io import UnsupportedOperation
from pathlib import Path
from typing import Literal, TypeAlias

import pytest

from pinnacle.constants import IMG_DIR
from pinnacle.ipfs.content.content import Content


@pytest.fixture
def img_path():
    filename = "han.png"
    return IMG_DIR / filename, filename


ImgPathFixture: TypeAlias = tuple[Path, Literal["han.png"]]


@pytest.fixture
def content(img_path: ImgPathFixture):
    path, _ = img_path
    return Content(path)


def test_content(content: Content):
    try:
        content.open()
    except:  # pragma: no cover
        pass
    else:
        assert content.opened
        assert content._bytes is not None
    finally:
        content.close()


def test_content_context_manager(img_path: ImgPathFixture):
    path, _ = img_path

    with Content(path) as content:
        assert content.opened
        assert content._bytes is not None

    assert content.closed


def test_reopen_fail(img_path: ImgPathFixture):
    path, _ = img_path

    with Content(path) as content:
        with pytest.raises(UnsupportedOperation):
            content.open()


def test_close_before_open(content: Content):
    with pytest.raises(UnsupportedOperation):
        content.close()
