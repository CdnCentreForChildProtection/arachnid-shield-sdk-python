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


TIMEOUT_WRITE_PERMISSIVE = httpx.Timeout(
    60,  # Default timeout for all operations unless otherwise stated.
    connect=3,  
    # Large chunks can take arbitrarily long to complete a write 
    # so wait arbitrarily long to finish writes.
    write=None,
)

TIMEOUT_READ_PERMISSIVE = httpx.Timeout(
    60,  # Default timeout for all operations unless otherwise stated.
    connect=3,
    # Allow the server enough time to process the request and to read the response back.
    read=60
)


class ArachnidShield(_ArachnidShield):
    """A client to communicate with the Arachnid Shield API
    provided by the Canadian Centre for Child Protection.

    """

    __client = httpx.Client

    def __init__(self, username: typing.Union[str, bytes], password: typing.Union[str, bytes]):
        super().__init__(username=username, password=password)
        self.__client = super()._build_sync_http_client()

    def scan_media_from_bytes(
        self, 
        contents: typing.Union[bytes, io.BytesIO], 
        mime_type: str,
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_WRITE_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            contents: The raw bytes that represent the media.
            mime_type: The mimetype of the media.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        return self.scan_media_from_bytes_with_config(ScanMediaFromBytes(contents=contents, mime_type=mime_type), timeout=timeout)

    def scan_media_from_file(
        self, 
        filepath: pathlib.Path, 
        mime_type_override: typing.Optional[str] = None, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_WRITE_PERMISSIVE,
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
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
                            f"`mime_type_override`."
                        )
                    )
                )

        with open(filepath, "rb") as f:
            contents = f.read()

        config = ScanMediaFromBytes(contents=contents, mime_type=mime_type)
        return self.scan_media_from_bytes_with_config(config, timeout=timeout)

    def scan_media_from_url(
        self, 
        url: str, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_READ_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            url: The absolute URL to scan.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        return self.scan_media_from_url_with_config(ScanMediaFromUrl(url=url), timeout=timeout)

    def scan_media_from_bytes_with_config(
        self, 
        config: ScanMediaFromBytes, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_WRITE_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            config: The context that will be used to build the request.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
            timeout=timeout,
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    def scan_media_from_url_with_config(
        self, 
        config: ScanMediaFromUrl, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_READ_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            config: The context that will be used to build the request.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
            timeout=timeout,
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    def scan_pdq_hashes(
        self, 
        config: ScanMediaFromPdq,
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_READ_PERMISSIVE,
    ) -> ScannedPDQHashes:
        """
        Scan medias for CSAM based on their PDQ hashes.
        Args:
            config: The context that will be used to build the request.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
            timeout=timeout,
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

    async def scan_media_from_bytes(
        self, 
        contents: typing.Union[bytes, io.BytesIO], 
        mime_type: str,
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_WRITE_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            contents: The raw bytes that represent the media.
            mime_type: The mimetype of the media.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """

        return await self.scan_media_from_bytes_with_config(ScanMediaFromBytes(contents=contents, mime_type=mime_type), timeout=timeout)

    async def scan_media_from_url(
        self, 
        url: str, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_READ_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            url: The absolute URL to scan.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

        Returns:
            The record of a successful media scan.

        Raises:
            `ArachnidShieldError` on a failed but complete interaction with
            the Arachnid Shield API, and `httpx.HTTPError` on any other connection failures.
        """
        return await self.scan_media_from_url_with_config(ScanMediaFromUrl(url=url), timeout=timeout)

    async def scan_media_from_file(
        self, 
        filepath: pathlib.Path, 
        mime_type_override: typing.Optional[str] = None, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_WRITE_PERMISSIVE,
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
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
                            f"`mime_type_override`."
                        )
                    )
                )

        with open(filepath, "rb") as f:
            contents = f.read()

        config = ScanMediaFromBytes(contents=contents, mime_type=mime_type)
        return await self.scan_media_from_bytes_with_config(config, timeout=timeout)

    async def scan_media_from_bytes_with_config(
        self, 
        config: ScanMediaFromBytes, 
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_WRITE_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the contents of some media, along with a mime type,
        scan the contents for matches against known child abuse media.

        Args:
            config: The context that will be used to build the request.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
            timeout=timeout,
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    async def scan_media_from_url_with_config(
        self, 
        config: ScanMediaFromUrl,
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_READ_PERMISSIVE,
    ) -> ScannedMedia:
        """Given the absolute url that hosts the media we wish to scan,
        scan the contents of that url for matches against known harmful content.

        Args:
            config: The context that will be used to build the request.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
            timeout=timeout,
        )

        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedMedia.from_dict(response.json())

    async def scan_pdq_hashes(
        self, 
        config: ScanMediaFromPdq,
        timeout: typing.Optional[httpx.Timeout] = TIMEOUT_READ_PERMISSIVE,
    ) -> ScannedPDQHashes:
        """
        Scan medias for CSAM based on their PDQ hashes.
        Args:
            config: The context that will be used to build the request.
            timeout:
                If provided, will set a timeout configuration for the underlying http client.

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
            timeout=timeout,
        )
        if response.is_client_error or response.is_server_error:
            error_detail = ErrorDetail.from_dict(response.json())
            raise ArachnidShieldException(error_detail)

        response.raise_for_status()
        return ScannedPDQHashes.from_dict(response.json())
