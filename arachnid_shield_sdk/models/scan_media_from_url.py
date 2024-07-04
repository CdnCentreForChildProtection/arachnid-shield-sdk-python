import typing
import dataclasses


@dataclasses.dataclass
class ScanMediaFromUrl:
    """A representation of a request to scan media from a url.

    Example:
        {
            "url": "https://protectchildren.ca/static/images/content/front-page/protected-banner.95ca6d527cb5.jpg"
        }

    Attributes:
        url (str):
            The url to get the media from.
    """

    url: str

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dataclasses.asdict(self)

    def _validate(self):
        if not isinstance(self.url, str):
            raise ValueError("argument `url` must be a `str`")

    def __post_init__(self):
        self._validate()

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "ScanMediaFromUrl":
        return cls(url=src_dict["url"])
