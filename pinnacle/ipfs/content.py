import posixpath
from dataclasses import dataclass, field
from typing import Any, Literal

from pinnacle.type_aliases import PathType

IPFS_GATEWAY = "https://ipfs.io/ipfs/{cid}"
LOCAL_GATEWAY = "http://127.0.0.1:8080/ipfs/{cid}"


@dataclass
class Content:
    """Content Object with IPFS object properties."""

    path: PathType
    mimetype: str = "application/octet-stream"
    pinned: bool = field(init=False, default=False)
    cid: str | None = field(init=False, default=None)

    @property
    def basename(self) -> str:
        return posixpath.basename(self.path)

    def read(self) -> bytes:
        with open(self.path, "rb") as file:
            return file.read()

    def format(self) -> dict[str, Any]:
        """Prepare a dict containing fields ready for pinning"""
        return dict(
            file=(
                self.basename,
                self.read(),
                self.mimetype,
            )
        )

    def gateway(self, type: Literal["ipfs", "local"] = "ipfs") -> str:
        """Generate an IPFS-compatible url to view content

        Args:
            type (str, optional): gateway type.
            Available options are "ipfs" and "local". Defaults to "ipfs".

        Raises:
            ValueError: if cid is None
            ValueError: if type is not a valid option
        """

        if not self.pinned:
            raise ValueError("Content is not pinned yet")

        if type == "local":
            return LOCAL_GATEWAY.format(cid=self.cid)
        elif type == "ipfs":
            return IPFS_GATEWAY.format(cid=self.cid)
        else:
            raise ValueError("Acceptable category: 'ipfs', 'local'")


# mimetype is Content_Type header.
# default value is "application/octet-stream"
