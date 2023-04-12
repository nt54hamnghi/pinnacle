from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Literal, TypeAlias

import httpx
from pydantic import BaseModel, Field

from pinnacle.ipfs.content.content import Content

from ..config import BearerAuth, Config
from ..model.model import Pin, PinResults, Status, TextMatchingStrategy

APIClient: TypeAlias = httpx.Client


class PinAPI(ABC):
    def __init__(
        self, api_client: APIClient, config: Config | None = None
    ) -> None:
        self.api_client = api_client
        self.config = Config() if config is None else config

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

    def _call_api(
        self,
        method: Literal["GET", "POST", "DELETE"],
        endpoint: str,
        **kwargs,
    ):
        request_params = self.config.setup() | kwargs
        url = f"{self.config.url}/{endpoint}"

        match method:
            case "GET":
                return self.api_client.get(url=url, **request_params)
            case "POST":
                return self.api_client.post(url=url, **request_params)
            case "DELETE":
                return self.api_client.delete(url=url, **request_params)
            case _:
                raise ValueError("Unsupported HTTP Method")


# cid: list[str] | None = None,
# name: str | None = None,
# match: TextMatchingStrategy | None = None,
# status: Status | None = None,
# before: datetime | None = None,
# after: datetime | None = None,
# limit: int | None = None,
# meta: dict[str, str] | None = None,
