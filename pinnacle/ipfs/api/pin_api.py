from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, ClassVar, Literal, TypeAlias

import httpx
from httpx._types import RequestFiles
from pydantic import BaseModel, Field

from pinnacle.ipfs.content.content import Content

from ..config import BearerAuth, Config
from ..model.model import Pin, PinResults, Status, TextMatchingStrategy


class APIClient:
    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    @staticmethod
    def _prepare(endpoint: str, config: Config, query_params: dict):
        request_params = {
            "url": f"{config.url}/{endpoint}",
            "params": query_params,
        }

        return request_params | config.setup()

    def get(self, endpoint: str, config: Config, query_params: dict):
        _params = self._prepare(endpoint, config, query_params)

        return self._client.get(**_params)

    def post(
        self,
        endpoint: str,
        config: Config,
        query_params: dict,
        files: RequestFiles | None = None,
    ):
        _params = self._prepare(endpoint, config, query_params)

        return self._client.post(**_params, files=files)


class PinAPI(ABC):
    global_config: ClassVar[Config]

    def __init__(
        self, client: httpx.Client, config: Config | None = None
    ) -> None:
        self.api_client = APIClient(client)
        self.config = self.global_config if config is None else config

    @abstractmethod
    def add(self, content: Content, cid_version: int = 1):
        ...

    # @abstractmethod
    def pin(self, pin: Pin):
        ...

    # @abstractmethod
    def get_pins(self):
        ...

    # @abstractmethod
    def get_pins_by_request_id(self):
        ...

    # @abstractmethod
    def replace_pins_by_request_id(self):
        ...

    # @abstractmethod
    def remove_pins_by_request_id(self):
        ...

    def authenticate_with_token(self, token: str):
        auth = BearerAuth(token)
        self.config.update_authentication(auth)

    def authenticate_with_env(self, env_name: str):
        auth = BearerAuth.from_env(env_name)
        self.config.update_authentication(auth)


# cid: list[str] | None = None,
# name: str | None = None,
# match: TextMatchingStrategy | None = None,
# status: Status | None = None,
# before: datetime | None = None,
# after: datetime | None = None,
# limit: int | None = None,
# meta: dict[str, str] | None = None,
