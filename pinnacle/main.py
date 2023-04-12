import httpx

from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.api.local_pin import LocalPinAPI
from pinnacle.ipfs.content.content import Content


def main():
    with httpx.Client() as client:
        with Content(IMG_DIR / "kai.png") as content:
            pin_api = LocalPinAPI(client)
            pin_api.add(content)
            print(content.gateway("local"))


if __name__ == "__main__":
    main()
