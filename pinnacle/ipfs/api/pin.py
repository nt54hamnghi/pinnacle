import logging
from typing import Optional

import httpx

from pinnacle.ipfs.config import Config
from pinnacle.ipfs.content import Content
from pinnacle.ipfs.api.pinner import Pin
from pinnacle.type_aliases import PathType

logging.basicConfig(level=logging.INFO)


def _pin(
    content: Content,
    config: Config,
    client: Optional[httpx.Client] = None,
) -> Content:
    config.pin.validate()

    request = config.setup()
    request["files"] = content.format()

    response = client.post(**request) if client else httpx.post(**request)
    response.raise_for_status()

    content.pinned = True
    content.cid = config.pin.get_cid(response)

    return content


def pin(
    path: PathType,
    pinner: Pin,
    client: Optional[httpx.Client] = None,
    mimetype: str | None = None,
    extra: Optional[dict] = None,
) -> Content:
    if extra is None:
        extra = dict()
    if mimetype is None:
        mimetype = pinner.content_type

    content = Content(path, mimetype)
    config = Config(pinner)
    config.update_params(extra)

    return _pin(content, config, client)
