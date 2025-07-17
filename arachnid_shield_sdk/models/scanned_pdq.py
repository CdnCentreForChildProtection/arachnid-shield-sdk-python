import dataclasses
import typing

from ..models.media_classification import MediaClassification
from ..models.scanned_media import NearMatchDetail, MatchType


@dataclasses.dataclass
class PDQMatch:
    """A record of a near match (based on perceptual hashing) of a PDQ hash to a known PDQ hash in our database.

    Attributes:
        classification:
            The classification of the media in our database.
        match_type:
            If a match exists, then 'near', otherwise null.
        near_match_details:
            If a match exists, then the details including the SHA1 and SHA256 hashes, otherwise null.
    """
    classification: MediaClassification
    match_type: typing.Optional[MatchType]
    near_match_details: typing.Optional[NearMatchDetail]

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "PDQMatch":
        near_match_details = src_dict.get("near_match_details")
        if near_match_details is not None:
            near_match_details = NearMatchDetail.from_dict(near_match_details)

        classification = src_dict.get("classification")
        if classification is not None:
            classification = MediaClassification(classification)
        return cls(
            classification=classification,
            match_type=MatchType.from_value(src_dict["match_type"]),
            near_match_details=near_match_details,
        )

    @property
    def matches_known_media(self) -> bool:
        """Determine whether the scanned media matches any known media."""
        return self.classification is not None and self.classification != MediaClassification.NoKnownMatch


@dataclasses.dataclass
class ScannedPDQHashes:
    """A record of a batch of PDQ hashes that have been scanned by the Arachnid Shield API
       and any matching classifications that were found in the database.

       Attributes:
           scanned_hashes:
               A dictionary of near matches keyed by the queried PDQs. If no match
               was found for a query PDQ, the value corresponding to the query PDQ is `null`.
    """
    scanned_hashes: typing.Dict[str, PDQMatch]

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        data = dataclasses.asdict(self)
        return data

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "ScannedPDQHashes":
        scanned_hashes = {}
        for key, value in src_dict["scanned_hashes"].items():
            near_match_details = value.get('near_match_details')
            if near_match_details is not None:
                near_match_details = NearMatchDetail.from_dict(near_match_details)
            scanned_hashes[key] = PDQMatch(
                classification=value['classification'],
                match_type=MatchType.from_value(value['match_type']),
                near_match_details=near_match_details
            )
        return cls(
            scanned_hashes=scanned_hashes
        )


@dataclasses.dataclass
class ScanMediaFromPdq:
    """A representation of a request to scan media using PDQ hashes.
       Attributes:
           hashes:
               A list of base64-encoded PDQ hashes to scan.
       """
    hashes: typing.List[str]

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "ScanMediaFromPdq":
        return cls(
            hashes=[pdq_hash for pdq_hash in src_dict["hashes"]]
        )
