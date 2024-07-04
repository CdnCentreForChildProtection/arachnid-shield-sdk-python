import typing
import dataclasses

from ..models.media_classification import MediaClassification


@dataclasses.dataclass
class MatchDetails:
    """A match object representing the image in the Arachnid Shield database that has the same cryptographic hash as the scanned image.

    Example:
        {
            'sha1_base32': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ723456',
            'sha256_hex': '2DB0DA447137B17D49988EEEFC5AD73A58EF9F28215078D1D2F4263423BC4508',
            'classification': 'csam',
            'distance': 10000
        }

    Attributes:
        sha1_base32 (str):
            The base-32 representation of the SHA1 cryptographic hash of the media.
        sha256_hex (str):
            The base-16 (hexadecimal) representation of the SHA256 cryptographic hash of the media.
        classification (Union[None, MediaClassification]):
            The classification assigned to this media.
        distance (int):
            The numeric distance between the two images. A distance below 5000 represents a close match; below 2000 is very close.
    """

    sha1_base32: str
    sha256_hex: str
    distance: int
    classification: typing.Optional[MediaClassification]

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        data = dataclasses.asdict(self)
        if self.classification is not None:
            data["classification"] = self.classification.value
        return data

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "MatchDetails":
        maybe_classification = src_dict.get("classification")
        classification = MediaClassification(maybe_classification) if maybe_classification else None
        return cls(
            sha256_hex=src_dict["sha256_hex"],
            sha1_base32=src_dict["sha1_base32"],
            distance=src_dict["distance"],
            classification=classification,
        )
