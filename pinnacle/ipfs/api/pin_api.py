from abc import ABC, abstractmethod
from typing import ClassVar

import httpx
from httpx._types import RequestFiles

from pinnacle.ipfs.content.content import Content

from ..config import BearerAuth, Config
from ..model.model import Pin


class PinAPI(ABC):
    global_config: ClassVar[Config]

    def __init__(self, config: Config | None = None) -> None:
        self.config = self.global_config if config is None else config
        self.api_client: httpx.Client | None = None

    @abstractmethod
    def add(self, content: Content, *, cid_version: int = 1):
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

    def register_client(self, client: httpx.Client):
        self.api_client = client

    def _prepare(self, endpoint: str, query_params: dict | None = None):
        request_params = {
            "url": f"{self.config.url}/{endpoint}",
            "params": query_params,
        }

        return request_params | self.config.setup()

    def _post(
        self,
        endpoint: str,
        *,
        files: RequestFiles | None = None,
        query_params: dict | None = None,
        client: httpx.Client | None = None,
    ):
        _params = self._prepare(endpoint, query_params)
        _client = client or self.api_client or httpx

        return _client.post(**_params, files=files)
