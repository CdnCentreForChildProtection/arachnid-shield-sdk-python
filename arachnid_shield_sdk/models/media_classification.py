from enum import Enum


class MediaClassification(str, Enum):
    """A list of the possible categories that an image or video could be classified as.

    Note: Video files are classified based on their frames. So, if
    any frame from a video matches a known `csam` image,
    the video will be classified as `csam`.  Similarly, if any frame
    matches a `harmful-abusive-material` image, the video will be classified
    as `harmful-abusive-material`.  If both `csam` and `harmful-abusive-material`
    frames are matched in a single video, the classification `csam`
    will be returned.

    More classification types may be added in the future.

    Attributes:
        CSAM:
            Child sexual abuse material, also known as "child pornography".
        HarmfulAbusiveMaterial:
            Content considered harmful to children includes all images or videos associated with the abusive incident, nude or partially nude images or videos of children that have become publicly available and are used in a sexualized context or connected to sexual commentary.
        NoKnownMatch:
            The media was not an exact match or near match to any classified CSAM or harmful/abusive material in our database.
    """

    CSAM = "csam"
    HarmfulAbusiveMaterial = "harmful-abusive-material"
    NoKnownMatch = "no-known-match"

    def __str__(self) -> str:
        return str(self.value)
