import posixpath
from posixpath import exists, isfile
from typing import Any, Optional

from attrs import define, field

from pinnacle.aliases.field import noninit
from pinnacle.aliases.typehint import GeneralPath


@define(eq=False, order=False)
class Content:
    """Content Object with IPFS object properties."""

    # mimetype is Content_Type header.
    # default value is "application/octet-stream"

    path: GeneralPath = field()
    mimetype: str = "application/octet-stream"
    pinned: bool = noninit(default=False)
    cid: Optional[str] = noninit(default=None)

    @path.validator
    def _check_path(self, attr, val):
        if not exists(val) or not isfile(val):
            raise FileNotFoundError

    @property
    def basename(self) -> str:
        """content's filename"""
        return posixpath.basename(self.path)

    def format(self) -> dict[str, Any]:
        """Prepare a dict containing fields ready for pinning"""
        return dict(file=(self.basename, self.read(), self.mimetype))

    def read(self) -> bytes:
        with open(self.path, "rb") as file:
            return file.read()

    def gateway(self, category: str = "ipfs") -> str:
        """Generate an IPFS-compatible url to view content
        Args:
            category (str, optional): gateway type.
            Available options are "ipfs" and "local".
            Defaults to "ipfs".

        Raises:
            ValueError: if content.cid is not set
            ValueError: if category is not the options
        """
        ipfs_gw = "https://ipfs.io/ipfs/{cid}"
        local_gw = "http://127.0.0.1:8080/ipfs/{cid}"

        if not self.pinned:
            raise ValueError("Content is not pinned yet!")
        if category == "local":
            return local_gw.format(cid=self.cid)
        elif category == "ipfs":
            return ipfs_gw.format(cid=self.cid)
        else:
            raise ValueError("Acceptable category: 'ipfs', 'local'")
