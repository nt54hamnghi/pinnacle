from pprint import pprint

import anyio

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.api.local_pin import AsyncLocalPin, LocalPin
from pinnacle.ipfs.content.content import AsyncContent, Content


def main():
    with LocalPin() as pin:
        with Content(IMG_DIR / "han.png") as content:
            pin_status = pin.add(content)
            print(content.gateway("local"))

            return pin_status


async def async_main():
    async with AsyncLocalPin() as apin:
        async with AsyncContent(IMG_DIR / "kai.png") as acontent:
            pin_status = await apin.add(acontent)
            print(acontent.gateway("local"))

            return pin_status


if __name__ == "__main__":
    pprint(main().json(exclude_none=True))
    pprint(anyio.run(async_main).json(exclude_none=True))
