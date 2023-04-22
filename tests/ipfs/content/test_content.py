from io import UnsupportedOperation
from pathlib import Path

import pytest

from pinnacle.ipfs.content.content import Content


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


def test_content_context_manager(path: Path):
    with Content(path) as content:
        assert content.opened
        assert content._bytes is not None

    assert content.closed


def test_reopen_fail(path: Path):
    with Content(path) as content:
        with pytest.raises(UnsupportedOperation):
            content.open()


def test_close_before_open(content: Content):
    with pytest.raises(UnsupportedOperation):
        content.close()
