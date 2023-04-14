from abc import ABC, abstractmethod
from typing import ClassVar, Literal

import httpx
from httpx._types import RequestFiles

from pinnacle.ipfs.content.content import Content
from pinnacle.ipfs.model.model import PinStatus

from ..config import BearerAuth, Config


class BasePinAPI:
    global_config: ClassVar[Config]

    def __init__(self, config: Config | None = None, *args, **kwds) -> None:
        self.config = self.global_config if config is None else config

    def _build_request_params(
        self, endpoint: str, query_params: dict | None = None
    ):
        request_params = {
            "url": f"{self.config.url}/{endpoint}",
            "params": query_params,
        }

        return request_params | self.config.setup()

    def authenticate_with_token(self, token: str):
        auth = BearerAuth(token)
        self.config.update_authentication(auth)

    def authenticate_with_env(self, env_name: str):
        auth = BearerAuth.from_env(env_name)
        self.config.update_authentication(auth)


class PinAPI(BasePinAPI, ABC):
    global_config: ClassVar[Config]

    def __init__(
        self,
        config: Config | None = None,
        api_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(config)
        self.api_client = api_client or httpx.Client()

    @abstractmethod
    def add(self, content: Content, *, cid_version: int = 1) -> PinStatus:
        ...

    def is_async_client(self):
        return isinstance(self, httpx.AsyncClient)

    def __enter__(self):
        self.api_client.__enter__()
        return self

    def __exit__(self, exc_type, exc_instance, traceback):
        return self.api_client.__exit__(exc_type, exc_instance, traceback)

    def _request(
        self,
        method: Literal["GET", "POST", "DELETE"],
        endpoint: str,
        query_params: dict | None = None,
        *args,
        **kwargs,
    ):
        _params = self._build_request_params(endpoint, query_params) | kwargs
        return self.api_client.request(method, *args, **_params)

    def _post(
        self,
        endpoint: str,
        *,
        files: RequestFiles | None = None,
        query_params: dict | None = None,
    ):
        return self._request("POST", endpoint, query_params, files=files)

    def _get(
        self,
        endpoint: str,
        *,
        query_params: dict | None = None,
    ):
        return self._request("GET", endpoint, query_params)


class AsyncPinAPI(BasePinAPI, ABC):
    global_config: ClassVar[Config]

    def __init__(
        self,
        config: Config | None = None,
        api_client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(config)
        self.api_client = api_client or httpx.AsyncClient()

    @abstractmethod
    async def add(
        self, content: Content, *, cid_version: int = 1
    ) -> PinStatus:
        ...

    async def __aenter__(self):
        await self.api_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_instance, traceback):
        return await self.api_client.__aexit__(
            exc_type, exc_instance, traceback
        )

    async def _request(
        self,
        method: Literal["GET", "POST", "DELETE"],
        endpoint: str,
        query_params: dict | None = None,
        *args,
        **kwargs,
    ):
        _params = self._build_request_params(endpoint, query_params) | kwargs
        return await self.api_client.request(method, *args, **_params)

    async def _post(
        self,
        endpoint: str,
        *,
        files: RequestFiles | None = None,
        query_params: dict | None = None,
    ):
        return await self._request(
            "POST", endpoint, query_params, files=files
        )

    async def _get(
        self,
        endpoint: str,
        *,
        query_params: dict | None = None,
    ):
        return await self._request("GET", endpoint, query_params)
