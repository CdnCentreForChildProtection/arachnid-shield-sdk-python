import typing
import os
import httpx


DEFAULT_BASE_URL = "https://shield.projectarachnid.com/"


class _ArachnidShield:
    __base_url: str
    __username: typing.Union[str, bytes]
    __password: typing.Union[str, bytes]

    def __init__(
        self,
        *,
        username: typing.Union[str, bytes],
        password: typing.Union[str, bytes],
        base_url: str = os.getenv("ARACHNID_SHIELD_URL", DEFAULT_BASE_URL),
    ):
        self.__base_url = base_url
        self.__username = username
        self.__password = password

    def _build_sync_http_client(self):
        return httpx.Client(auth=httpx.BasicAuth(username=self.__username, password=self.__password))

    def _build_async_http_client(self):
        return httpx.AsyncClient(auth=httpx.BasicAuth(username=self.__username, password=self.__password))

    @property
    def base_url(self):
        return self.__base_url
