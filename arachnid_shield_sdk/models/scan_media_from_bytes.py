import dataclasses
import io
import typing


@dataclasses.dataclass
class ScanMediaFromBytes:
    """A representation of a request to scan media from bytes.

    Example:
        {
            'contents': b'0x00',
            'mime_type': 'image/jpeg'
        }

    Attributes:
        contents (Union[bytes, io.BytesIO]):
            The raw contents of the media.
        mime_type (str):
            The mime type of the media.
    """

    contents: typing.Union[bytes, io.BytesIO]
    mime_type: str

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {"contents": self.contents, "mime_type": self.mime_type}

    def _validate(self):
        if not isinstance(self.mime_type, str):
            raise ValueError("argument `mime_type` must be a `str`")

        if not isinstance(self.contents, bytes) and not isinstance(self.contents, io.BytesIO):
            raise ValueError("argument `contents` must be one of `bytes` or `io.BytesIO`")

        if isinstance(self.contents, io.BytesIO):
            self.contents = self.contents.read()

    def __post_init__(self):
        self._validate()

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "ScanMediaFromBytes":
        mime_type = src_dict["mime_type"]
        contents = src_dict["contents"]

        return cls(mime_type=mime_type, contents=contents)
