import typing
import dataclasses

import httpx


@dataclasses.dataclass
class ErrorDetail:
    """A container for any error messages that the Arachnid Shield API sends us.

    Example:
        {
            "detail": "oops. something went wrong and here's a little more info about it."
        }

    Attributes:
        detail (str):
            An error message in the container
    """

    detail: str

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "ErrorDetail":
        return cls(
            detail=src_dict["detail"],
        )


class ArachnidShieldException(httpx.HTTPError):
    """Raised on an unsuccessful interaction with the ArachnidShield API."""

    __detail: typing.Optional[ErrorDetail] = None

    def __init__(self, detail: ErrorDetail):
        self.__detail = detail

    @property
    def detail(self) -> ErrorDetail:
        return self.__detail

    def __str__(self):
        return self.detail.detail
