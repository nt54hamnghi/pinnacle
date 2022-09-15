import logging
from typing import Optional

import httpx

from pinnacle.aliases.typehint import GeneralPath, NoneableStr
from pinnacle.ipfs.config import Config
from pinnacle.ipfs.content import Content
from pinnacle.ipfs.pinner import Pin

logging.basicConfig(level=logging.INFO)


def _pin(
    content: Content,
    pinner: Pin,
    config: Config,
    client: Optional[httpx.Client] = None,
) -> Content:

    # pinner.validate()

    request = config.setup()
    request["files"] = content.format()

    response = client.post(**request) if client else httpx.post(**request)
    response.raise_for_status()

    content.pinned = True
    content.cid = pinner.get_cid(response)

    return content


def pin(
    path: GeneralPath,
    pinner: Pin,
    client: Optional[httpx.Client] = None,
    mimetype: NoneableStr = None,
    extra: Optional[dict] = None,
) -> Content:
    if extra is None:
        extra = dict()
    if mimetype is None:
        mimetype = pinner.content_type

    content = Content(path, mimetype)
    config = Config(pinner)
    config.update_params(extra)

    return _pin(content, pinner, config, client)
