import httpx

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.api.local_pin import LocalPin
from pinnacle.ipfs.content.content import Content


def main():
    with httpx.Client() as client:
        with Content(IMG_DIR / "han.png") as content:
            LocalPin(client).add(content)

            print(content.gateway("local"))


if __name__ == "__main__":
    main()
