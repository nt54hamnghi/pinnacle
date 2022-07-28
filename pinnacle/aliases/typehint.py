from pathlib import Path
from typing import Optional, TypeVar, Union


RealNumber = Union[int, float]

NoneableStr = Optional[str]  # optional string
GeneralPath = Union[Path, str]  # general path
GeneralT = TypeVar("GeneralT")  # generic type var
