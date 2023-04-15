from pprint import pprint

import anyio

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.api.local_pin import AsyncLocalPin, LocalPin
from pinnacle.ipfs.api.nft_storage import AsyncNFTStorage, NFTStorage
from pinnacle.ipfs.api.pin_api import AsyncPinAPI, PinAPI
from pinnacle.ipfs.api.pinata import AsyncPinata, Pinata
from pinnacle.ipfs.content.content import AsyncContent, Content


def main(Pinner: type[PinAPI]):
    with Pinner() as pin:
        with Content(IMG_DIR / "han.png") as content:
            pin_status = pin.add(content)
            print(content.gateway("local"))

            return pin_status


async def async_main(Pinner: type[AsyncPinAPI]):
    async with Pinner() as apin:
        async with AsyncContent(IMG_DIR / "kai.png") as acontent:
            pin_status = await apin.add(acontent)
            print(acontent.gateway("local", "subdomain"))

            return pin_status


if __name__ == "__main__":
    response = main(NFTStorage)
    pprint(response)

    response = anyio.run(async_main, AsyncNFTStorage)
    pprint(response)
