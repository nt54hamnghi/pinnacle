import logging
from typing import Optional

import httpx

from pinnacle.aliases.typehint import GeneralPath, NoneableStr
from pinnacle.ipfs.configuration import Configuration
from pinnacle.ipfs.content import Content
from pinnacle.ipfs.pinner import AbstractPin

logging.basicConfig(level=logging.INFO)


def _pin(
    content: Content,
    pinner: AbstractPin,
    config: Configuration,
    client: Optional[httpx.Client] = None,
) -> Content:

    pinner.validate()

    request = config.setup()
    request["files"] = content.format()

    response = client.post(**request) if client else httpx.post(**request)
    response.raise_for_status()

    content.pinned = True
    content.cid = pinner.get_cid(response)

    return content


def pin(
    path: GeneralPath,
    pinner: AbstractPin,
    client: Optional[httpx.Client] = None,
    mimetype: NoneableStr = None,
    meta: dict = dict(),
) -> Content:
    if mimetype is None:
        mimetype = pinner.content_type

    content = Content(path, mimetype)
    config = Configuration.from_pin(pinner).update(meta)

    return _pin(content, pinner, config, client, meta)
