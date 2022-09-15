import os
from typing import Any, Generator, Optional

import httpx
from attrs import define, field
from dotenv import dotenv_values
from httpx import Request, Response

from pinnacle.aliases.typehint import NoneableStr
from pinnacle.ipfs.pinner import Pin


class ENVNotFound(KeyError):
    pass


class AuthKeyNotFound(ENVNotFound):
    pass


def _from_os_env(keyname: str) -> str:
    if (env_var := os.getenv(keyname)) is None:
        raise ENVNotFound(keyname)
    return env_var


def _from_dot_env(keyname: str) -> str:
    try:
        return dotenv_values(".env")[keyname]
    except KeyError:
        raise ENVNotFound(keyname)


class Authentication(httpx.Auth):
    def __init__(self, token: NoneableStr = None):
        self.token = token

    @property
    def body(self) -> Optional[dict]:
        """Authentication property. Formated to be ready for request"""
        return f"Bearer {self.token}" if self.token else None

    @classmethod
    def from_env(cls, keyname: str):
        """Alternative constructor to load from environment variable"""
        try:
            return cls(_from_dot_env(keyname))
        except ENVNotFound:
            try:
                return cls(_from_os_env(keyname))
            except ENVNotFound:
                raise AuthKeyNotFound

    def auth_flow(
        self, request: Request
    ) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self.body
        yield request


@define(eq=False, order=False)
class Config:

    # the extra_params attribute includes optional arguments of httpx methods.
    # A complete list: https://www.python-httpx.org/api/#helper-functions

    pin: Pin
    auth: Optional[Authentication] = None
    extra_params: dict = field(factory=dict)

    def __attrs_post_init__(self):
        _keyname = self.pin.keyname
        if self.auth is None and _keyname is not None:
            self.auth = Authentication.from_env(_keyname)

    @property
    def no_auth(self) -> bool:
        return self.auth is None

    def load_auth(self, keyname: str) -> None:
        self.auth = Authentication.from_env(keyname)

    def update_params(self, params: dict[str, Any]) -> None:
        self.extra_params.update(params)

    def setup(self) -> dict[str, Any]:
        """Setup a parameter dict ready for httpx operation"""

        self.update_params({"url": self.pin.url})

        if not self.no_auth:
            self.update_params({"auth": self.auth})
        return self.extra_params
