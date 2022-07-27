import os
from typing import Any, Generator, Optional

import httpx
from attrs import define
from dotenv import dotenv_values
from httpx import Request, Response

from pinnacle.aliases.field import noneable, string
from pinnacle.aliases.typehint import GeneralT, NoneableStr
from pinnacle.ipfs.pinner import AbstractPin


class Authentication(httpx.Auth):
    def __init__(self, token: NoneableStr = None):
        self.token = token

    @property
    def body(self) -> Optional[dict]:
        """Authentication property. Formated to be ready for request"""
        return f"Bearer {self.token}" if self.token else None

    @classmethod
    def from_env(cls, keyname: str) -> str:
        """Alternative constructor
        Args:
            keyname (str): key to pass in 'load_environment_config'
        Raises:
            AuthenticationKeyNotFound: if failed to load
        """
        try:
            return cls(load_environment_config(keyname, "dotenv"))
        except EnvironmentVariableNotFound:
            try:
                return cls(load_environment_config(keyname, "environment"))
            except EnvironmentVariableNotFound:
                raise AuthenticationKeyNotFound

    def auth_flow(
        self, request: Request
    ) -> Generator[Request, Response, None]:
        request.headers["Authorization"] = self.body
        yield request


def not_empty(inst, attr, val):
    if val is not None and len(val) <= 0:
        raise ValueError(f"{attr} cannot be empty")


@define(eq=False, order=False)
class Configuration:

    # the meta attribute includes optional arguments of httpx methods.
    # A complete list: https://www.python-httpx.org/api/#helper-functions

    url: str = string()
    token: NoneableStr = noneable(validator=not_empty)
    keyname: NoneableStr = noneable(validator=not_empty)
    meta: dict = dict()
    auth: Optional[Authentication] = noneable(init=False)

    def __attrs_post_init__(self):
        if self.token is not None:
            self.auth = Authentication(self.token)
        if self.keyname is not None:
            self.auth = Authentication.from_env(self.keyname)

    @classmethod
    def from_pin(cls, pinner: AbstractPin):
        """Alternative constructor using a Pin object"""
        return cls(url=pinner.url, keyname=pinner.keyname)

    @property
    def no_auth(self) -> bool:
        return self.auth is None

    def update(self: GeneralT, meta: dict) -> GeneralT:
        self.meta = meta
        return self

    def setup(self) -> dict[str, Any]:
        """Setup a parameter dict ready for httpx operation"""
        params = {**dict(url=self.url), **self.meta}
        if not self.no_auth:
            params["auth"] = self.auth
        return params


def load_environment_config(keyname: str, source: str = "dotenv") -> str:
    """Load environment variables either from system or the .env file

    Args:
        keyname (str): key name
        source (str, optional): source to load form.
        Defaults to "dotenv". Possible values: "dotenv", "environment"

    Raises:
        EnvironmentVariableNotFound: when key is not found
        ValueError: when key is empty
        ValueError: when source is not the possible values

    Returns:
        str: authentication key
    """
    if len(keyname) <= 0:
        raise ValueError("key cannot be empty")
    if source == "environment":
        if (env_var := os.getenv(keyname)) is None:
            raise EnvironmentVariableNotFound(keyname)
        return env_var
    elif source == "dotenv":
        try:
            return dotenv_values(".env")[keyname]
        except KeyError:
            raise EnvironmentVariableNotFound(keyname)
    else:
        raise ValueError(
            "Incorrect source. Possible value: environment, dotenv"
        )


class EnvironmentVariableNotFound(KeyError):
    pass


class AuthenticationKeyNotFound(EnvironmentVariableNotFound):
    pass
