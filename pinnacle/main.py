from pinnacle.consts.dirs import IMG_DIR
from pinnacle.ipfs.api.local_pin import LocalPin
from pinnacle.ipfs.content.content import Content


def main():
    with LocalPin() as pin:
        with Content(IMG_DIR / "han.png") as content:
            pin.add(content)

            print(content.gateway("local"))


if __name__ == "__main__":
    main()
