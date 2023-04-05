import os
from typing import Any, Generator, Self

import httpx
from dotenv import dotenv_values
from httpx import Request, Response

from pinnacle.consts.pin_service import LOCAL_SERVICE


class ENVNotFound(KeyError):
    pass


class AuthKeyNotFound(ENVNotFound):
    pass


def _from_os_env(keyname: str) -> str:
    if (env_var := os.getenv(keyname)) is None:
        raise ENVNotFound(keyname)
    return env_var


def _from_dot_env(keyname: str):
    try:
        return dotenv_values(".env")[keyname]
    except KeyError:
        raise ENVNotFound(keyname)


class BearerAuth(httpx.Auth):
    def __init__(self, token: str | None = None):
        self.token = token

    @property
    def bearer_token(self) -> str | None:
        """Authentication property. Formated to be ready for request"""
        return f"Bearer {self.token}" if self.token else None

    def auth_flow(
        self, request: Request
    ) -> Generator[Request, Response, None]:
        if self.bearer_token:
            request.headers["Authorization"] = self.bearer_token
        yield request

    @classmethod
    def from_env(cls, keyname: str) -> Self:
        """Alternative constructor to load from environment variable"""
        try:
            return cls(_from_dot_env(keyname))
        except ENVNotFound:
            try:
                return cls(_from_os_env(keyname))
            except ENVNotFound:
                raise AuthKeyNotFound


class Config:
    def __init__(
        self,
        url: str = LOCAL_SERVICE,
        auth: httpx.Auth | None = None,
        extra_params: dict[str, Any] | None = None,
    ) -> None:
        self.url = url
        self.auth = auth
        # extra_params is optional arguments of httpx methods.
        # https://www.python-httpx.org/api/#helper-functions
        self.extra_params = {} if extra_params is None else extra_params

    @property
    def no_auth(self) -> bool:
        return self.auth is None

    def update_params(self, params: dict[str, Any]) -> None:
        self.extra_params.update(params)

    def setup(self) -> dict[str, Any]:
        """Setup a parameter dict ready for httpx operation"""
        self.update_params({"url": self.url})
        if self.auth:
            self.update_params({"auth": self.auth})

        return self.extra_params

    # def init_auth(self, keyname: str) -> None:
    #     self.auth = httpx.Auth.from_env(keyname)
