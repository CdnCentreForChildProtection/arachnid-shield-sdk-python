import io
import mimetypes
import pathlib
import typing
import urllib.parse

import httpx

from ..api.client import _ArachnidShield
from ..models import (
    ScannedMedia,
    ErrorDetail,
    ArachnidShieldException,
    ScanMediaFromUrl,
    ScanMediaFromBytes,
    ScanMediaFromPdq,
    ScannedPDQHashes
)


class ArachnidShield(_ArachnidShield):
    """A client to communicate with the Arachnid Shield API
    provided by the Canadian Centre for Child Protection.

    """

    __client = httpx.Client

    def __init__(self, username: typing.Union[str, bytes], password: typing.Union[str, bytes]):
        super().__init__(username=username, password=password)
        self.__client = super()._build_sync_http_client()

    def scan_media_from_bytes(self, contents: typing.Union[bytes, io.BytesIO], mime_type: str) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            contents: The raw bytes that represent the media.
            mime_type: The mimetype of the media.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        return self.scan_media_from_bytes_with_config(ScanMediaFromBytes(contents=contents, mime_type=mime_type))

    def scan_media_from_file(
            self, filepath: pathlib.Path, mime_type_override: typing.Optional[str] = None
    ) -> ScannedMedia:
        """Given path to the media file to scan, and an optional
        value for mime_type that bypasses guessing it based of the filepath,
        scan the media stored at that file for matches against known harmful content.

        Args:
            filepath:
                The path to the file to be scanned.
            mime_type_override:
                If provided, will use this as the mime_type
                instead of guessing it from the filepath.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        mime_type = mime_type_override
        if mime_type is None:
            mime_type, _encoding = mimetypes.guess_type(filepath)
            if mime_type is None:
                raise ArachnidShieldException(
                    ErrorDetail(
                        detail=(
                            f"Failed to identify mime_type for {filepath}. "
                            f"You may specify it explicitly by providing "
                            f"`force_mime_type`."
                        )
                    )
                )

        with open(filepath, "rb") as f:
            contents = f.read()

        config = ScanMediaFromBytes(contents=contents, mime_type=mime_type)
        return self.scan_media_from_bytes_with_config(config)

    def scan_media_from_url(self, url: str) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            url: The absolute URL to scan.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        return self.scan_media_from_url_with_config(ScanMediaFromUrl(url=url))

    def scan_media_from_bytes_with_config(self, config: ScanMediaFromBytes) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            config: The context that will be used to build the request.

        Returns:
            ScannedMedia: A record of a successful scan of the media.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        url = urllib.parse.urljoin(self.base_url, "v1/media/")

        response = self.__client.post(
            url=url,
            headers={"Content-Type": config.mime_type},
            content=config.contents,
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    def scan_media_from_url_with_config(self, config: ScanMediaFromUrl) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            config: The context that will be used to build the request.

        Returns:
            ScannedMedia: A record of a successful scan of the media.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        _url = urllib.parse.urljoin(self.base_url, "v1/url/")

        response = self.__client.post(
            url=_url,
            headers={"Content-Type": "application/json"},
            json=config.to_dict(),
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    def scan_pdq_hashes(self, config: ScanMediaFromPdq) -> ScannedPDQHashes:
        """
        Scan medias for CSAM based on their PDQ hashes.
        Args:
            config: The context that will be used to build the request.

        Returns:
            ScannedPDQHashes: A record of a batch of PDQ hashes that have been scanned by the Arachnid Shield API
            and any matching classifications that were found in the database.

        Raises:
            `ArachnidShieldException` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        _url = urllib.parse.urljoin(self.base_url, "v1/pdq/")
        response = self.__client.post(
            url=_url,
            headers={"Content-Type": "application/json"},
            json=config.to_dict(),
        )
        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedPDQHashes.from_dict(response.json())


class ArachnidShieldAsync(_ArachnidShield):
    """An asynchronous client to communicate with the Arachnid Shield API
    provided by the Canadian Centre for Child Protection.
    """

    __client = httpx.AsyncClient

    def __init__(self, username: typing.Union[str, bytes], password: typing.Union[str, bytes]):
        super().__init__(username=username, password=password)
        self.__client = super()._build_async_http_client()

    async def scan_media_from_bytes(self, contents: typing.Union[bytes, io.BytesIO], mime_type: str) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            contents: The raw bytes that represent the media.
            mime_type: The mimetype of the media.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        return await self.scan_media_from_bytes_with_config(ScanMediaFromBytes(contents=contents, mime_type=mime_type))

    async def scan_media_from_url(self, url: str) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            url: The absolute URL to scan.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        return await self.scan_media_from_url_with_config(ScanMediaFromUrl(url=url))

    async def scan_media_from_file(
            self, filepath: pathlib.Path, mime_type_override: typing.Optional[str] = None
    ) -> ScannedMedia:
        """Given path to the media file to scan, and an optional
        value for mime_type that bypasses guessing it based of the filepath,
        scan the media stored at that file for matches against known harmful content.

        Args:
            filepath:
                The path to the file to be scanned.
            mime_type_override:
                If provided, will use this as the mime_type
                instead of guessing it from the filepath.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        mime_type = mime_type_override
        if mime_type is None:
            mime_type, _encoding = mimetypes.guess_type(filepath)
            if mime_type is None:
                raise ArachnidShieldException(
                    ErrorDetail(
                        detail=(
                            f"Failed to identify mime_type for {filepath}. "
                            f"You may specify it explicitly by providing "
                            f"`force_mime_type`."
                        )
                    )
                )

        with open(filepath, "rb") as f:
            contents = f.read()

        config = ScanMediaFromBytes(contents=contents, mime_type=mime_type)
        return await self.scan_media_from_bytes_with_config(config)

    async def scan_media_from_bytes_with_config(self, config: ScanMediaFromBytes) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            config: The context that will be used to build the request.

        Returns:
            ScannedMedia: A record of a successful scan of the media.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        url = urllib.parse.urljoin(self.base_url, "v1/media/")

        response = await self.__client.post(
            url=url,
            headers={"Content-Type": config.mime_type},
            content=config.contents,
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    async def scan_media_from_url_with_config(self, config: ScanMediaFromUrl) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            config: The context that will be used to build the request.

        Returns:
            ScannedMedia: A record of a successful scan of the media.

        Raises:
            `ArachnidShieldException` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        _url = urllib.parse.urljoin(self.base_url, "v1/url/")

        response = await self.__client.post(
            url=_url,
            headers={"Content-Type": "application/json"},
            json=config.to_dict(),
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    async def scan_pdq_hashes(self, config: ScanMediaFromPdq) -> ScannedPDQHashes:
        """
        Scan medias for CSAM based on their PDQ hashes.
        Args:
            config: The context that will be used to build the request.

        Returns:
            ScannedPDQHashes: A record of a batch of PDQ hashes that have been scanned by the Arachnid Shield API
            and any matching classifications that were found in the database.

        Raises:
            `ArachnidShieldException` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        _url = urllib.parse.urljoin(self.base_url, "v1/pdq/")
        response = await self.__client.post(
            url=_url,
            headers={"Content-Type": "application/json"},
            json=config.to_dict(),
        )
        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedPDQHashes.from_dict(response.json())
