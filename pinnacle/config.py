import pathlib

# directory configs
ROOT_DIR = pathlib.Path(__file__).parents[1]
METADATA_DIR = ROOT_DIR / "metadata"
IMG_DIR = ROOT_DIR / "img"

print(ROOT_DIR)
