import dataclasses
import typing
from enum import Enum

from ..models.media_classification import MediaClassification


class MatchType(str, Enum):
    """The technology that was used to verify a match between two media.

    This indicates whether the submitted media matched media in our database exactly
    (by cryptographic hash) or visually (by visual hash).

    Attributes:
        Exact:
            An exact cryptographic hash match using SHA1
        Near:
            A visual near-match using PhotoDNA
    """

    Exact = "exact"
    Near = "near"

    @classmethod
    def from_value(cls, value: typing.Optional[str]) -> typing.Optional["MatchType"]:
        if value is None:
            return None
        return cls(value)


@dataclasses.dataclass
class NearMatchDetail:
    """A record of a near match (based on perceptual hashing) to a known image in our database.

    Attributes:
        timestamp:
            The time, in seconds, in the submitted video file where the near match was found. For still images this will be 0.0.
        sha1_base32:
            The base-32 representation of the SHA1 cryptographic hash of the media in our database.
        sha256_hex:
            The base-16 (hexadecimal) representation of the SHA256 cryptographic hash of the media in our database.
        classification:
            The classification of the media in our database.
    """

    timestamp: float
    sha1_base32: str
    sha256_hex: str
    classification: typing.Optional[MediaClassification]

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        data = dataclasses.asdict(self)
        if self.classification is not None:
            data["classification"] = self.classification.value

        return data

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "NearMatchDetail":
        return cls(
            timestamp=src_dict["timestamp"],
            sha1_base32=src_dict["sha1_base32"],
            sha256_hex=src_dict["sha256_hex"],
            classification=src_dict["classification"],
        )



@dataclasses.dataclass
class ScannedMedia:
    """A record of a media (+ metadata) that has been scanned by the Arachnid Shield API
    and any matching classification that was found in our database.

    Attributes:
        size_bytes:
            The total size, in bytes, of the media that was scanned.
        sha1_base32:
            The base-32 representation of the SHA1 cryptographic hash of the media that was scanned.
        sha256_hex:
            The base-16 (hexadecimal) representation of the SHA256 cryptographic hash of the media that was scanned.
        classification:
            The classification of the media in our database that matched the submitted media
        match_type:
            The matching technology that was used to match the submitted media to the media in our
            database; `null` if the classification is `no-known-match`.
        near_match_details:
            A record of a near match (based on perceptual hashing) to a known image in our database .
    """

    size_bytes: int
    sha1_base32: str
    sha256_hex: str
    classification: typing.Optional[MediaClassification] = dataclasses.field(default=None)
    match_type: typing.Optional[MatchType] = dataclasses.field(default=None)
    near_match_details: typing.List[NearMatchDetail] = dataclasses.field(default_factory=list)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        data = dataclasses.asdict(self)
        if self.classification is not None:
            data["classification"] = self.classification.value

        return data

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "ScannedMedia":
        near_match_details = src_dict.get("near_match_details")
        if near_match_details is not None:
            near_match_details = [
                NearMatchDetail.from_dict(near_match_detail) for near_match_detail in near_match_details
            ]
        classification = src_dict.get("classification")
        if classification is not None:
            classification = MediaClassification(classification)
        return cls(
            sha256_hex=src_dict["sha256_hex"],
            sha1_base32=src_dict["sha1_base32"],
            size_bytes=src_dict["size_bytes"],
            classification=classification,
            match_type=MatchType.from_value(src_dict["match_type"]),
            near_match_details=near_match_details,
        )

    @property
    def matches_known_media(self) -> bool:
        """Determine whether the scanned media matches any known media."""
        return self.classification is not None and self.classification != MediaClassification.NoKnownMatch
