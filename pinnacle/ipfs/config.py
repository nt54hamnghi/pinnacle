import os
from typing import Any, Generator, Self

import httpx
from dotenv import dotenv_values
from httpx import Request, Response

from pinnacle.constants.pin_services import LOCAL_SERVICE


class ENVNotFoundError(KeyError):
    pass


class AuthKeyNotFoundError(ENVNotFoundError):
    pass


def _from_os_env(env_name: str) -> str:
    if (env_var := os.getenv(env_name)) is None:
        raise ENVNotFoundError(env_name)
    return env_var


def _from_dot_env(env_name: str):
    try:
        return dotenv_values(".env")[env_name]
    except KeyError:
        raise ENVNotFoundError(env_name)


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
    def from_env(cls, env_name: str) -> Self:
        """Alternative constructor to load from environment variable"""
        try:
            return cls(_from_dot_env(env_name))
        except ENVNotFoundError:
            try:
                return cls(_from_os_env(env_name))
            except ENVNotFoundError:
                raise AuthKeyNotFoundError


class Config:
    def __init__(
        self,
        url: str = LOCAL_SERVICE,
        auth: httpx.Auth | None = None,
        extra_params: dict[str, Any] | None = None,
        authless: bool = False,
    ) -> None:
        self.url = url
        self.auth = auth
        self.authless = authless
        # extra_params is optional arguments of httpx methods.
        # https://www.python-httpx.org/api/#helper-functions
        self.extra_params = {} if extra_params is None else extra_params

    def update_authentication(self, auth: BearerAuth):
        if self.authless:
            raise ValueError(
                "Cannot update authentication with an auth-less configuration"
            )
        self.auth = auth

    def update_params(self, params: dict[str, Any]) -> None:
        self.extra_params.update(params)

    def setup(self) -> dict[str, Any]:
        """Setup a parameter dict ready for httpx operation"""
        if self.auth:
            self.update_params({"auth": self.auth})

        return self.extra_params
