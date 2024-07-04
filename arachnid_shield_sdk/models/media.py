import typing
import dataclasses

from ..models.media_classification import MediaClassification


@dataclasses.dataclass
class Media:
    """Representation of a media.

    Example:
        {'sha1_base32': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ723456', 'sha256_hex':
            '2DB0DA447137B17D49988EEEFC5AD73A58EF9F28215078D1D2F4263423BC4508', 'classification': 'csam'}

    Attributes:
        sha1_base32 (str):
            The base-32 representation of the SHA1 cryptographic hash of the media.
        sha256_hex (str):
            The base-16 (hexadecimal) representation of the SHA256 cryptographic hash of the media.
        classification (Union[None, MediaClassification]):
            The classification assigned to this media.
    """

    sha1_base32: str
    sha256_hex: str
    classification: typing.Optional[MediaClassification] = dataclasses.field(default=None)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        sha1_base32 = self.sha1_base32
        sha256_hex = self.sha256_hex

        return {
            "sha1_base32": sha1_base32,
            "sha256_hex": sha256_hex,
            "classification": self.classification and self.classification.value,
        }

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "Media":
        return cls(
            sha1_base32=src_dict["sha1_base32"],
            sha256_hex=src_dict["sha256_hex"],
            classification=(
                src_dict["classification"] if ("classification" in src_dict and src_dict["classification"]) else None
            ),
        )
