import typing

import dataclasses

from ..models.match_details import MatchDetails


@dataclasses.dataclass
class VisualMatchDetails:
    """An array of images found in the Arachnid Shield database that were visually similar to the scanned image.

    Example:
    {
        'timestamp': 1688101421.123,
        'matches': [
            {
                'sha1_base32': '4523EFGHIJKLMNOPQRSTUVWXYZ723456',
                'sha256_hex': 'ABCDDA447137B17D49988EEEFC5AD73A58EF9F28215078D1D2F4263423BC4508',
                'classification': 'csam',
                'distance': 1300
            }
        ]
    }
    Attributes:
        timestamp (float):
            The time, in seconds, in the submitted video file where the match was found. For still images this will be 0.
        matches (List[MatchDetails]):
            A list containing 1 or more match objects representing the matched images in the Arachnid Shield database.
    """

    timestamp: float
    matches: typing.List["MatchDetails"] = dataclasses.field(default_factory=list)

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {"timestamp": self.timestamp, "matches": [match.to_dict() for match in self.matches]}

    @classmethod
    def from_dict(cls, src_dict: typing.Dict[str, typing.Any]) -> "VisualMatchDetails":
        from ..models.match_details import MatchDetails

        return cls(
            timestamp=src_dict["timestamp"], matches=[MatchDetails.from_dict(match) for match in src_dict["matches"]]
        )
