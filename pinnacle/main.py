from pprint import pprint
from typing import Callable

import anyio

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.api.local_pin import AsyncLocalPin, LocalPin
from pinnacle.ipfs.api.nft_storage import AsyncNFTStorage, NFTStorage
from pinnacle.ipfs.api.pin_api import AsyncPinAPI, PinAPI
from pinnacle.ipfs.api.pinata import AsyncPinata, Pinata
from pinnacle.ipfs.content.content import AsyncContent, Content


def pin(Pinner: type[PinAPI], env: str | None = None, verbose: bool = True):
    with Pinner() as pin_api:

        if not pin_api.authless:
            pin_api.authenticate_with_env(env)

        with Content(IMG_DIR / "han.png") as content:
            pin_status = pin_api.add(content)

            if verbose:
                print("\n", content.gateway("local"), end="\n\n")

            return pin_status


async def async_pin(
    Pinner: type[AsyncPinAPI], env: str | None = None, verbose: bool = True
):
    async with Pinner() as pin_api:

        if not pin_api.authless:
            pin_api.authenticate_with_env(env)

        async with AsyncContent(IMG_DIR / "kai.png") as content:
            pin_status = await pin_api.add(content)

            if verbose:
                print("\n", content.gateway("local"), end="\n\n")

            return pin_status


def local():
    response = pin(LocalPin)
    pprint(response)

    async_response = anyio.run(async_pin, AsyncLocalPin)
    pprint(async_response)


def pinata():
    response = pin(Pinata, env="PINATA_JWT")
    pprint(response)

    async_response = anyio.run(async_pin, AsyncPinata, "PINATA_JWT")
    pprint(async_response)


def nft_storage():
    response = pin(NFTStorage, env="NFT_STORAGE_JWT")
    pprint(response)

    async_response = anyio.run(async_pin, AsyncNFTStorage, "NFT_STORAGE_JWT")
    pprint(async_response)


def main(func: Callable):
    func()


if __name__ == "__main__":
    main(pinata)
