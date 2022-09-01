"""Package for making catalog of dataservices available in an API."""
import logging
from typing import Any, List, Optional


DEFAULT_CONTENT_TYPE = {"text": "text/turtle", "application": "application/rdf+xml"}
SUPPORTED_CONTENT_TYPES = [
    "text/turtle",
    "application/ld+json",
    "application/rdf+xml",
    "application/n-triples",
]


class InvalidMediaRangeError(ValueError):
    """Exception for invalid media ranges."""

    pass


class WeightedMediaRange:
    """Class for handling weighted media ranges."""

    def __init__(self, media_range: str, q: float = 1.0) -> None:
        """Initialize the weighted media range."""
        try:
            self.type, self.sub_type = media_range.split("/")
        except ValueError as e:
            raise InvalidMediaRangeError(f"Invalid media range: {media_range}") from e
        self.q = q

    def __eq__(self, other: Any) -> bool:  # pragma: no cover
        """Compare two weighted media ranges."""
        if isinstance(other, str):
            return f"{self.type}/{self.sub_type}" == other
        if isinstance(other, WeightedMediaRange):
            return self.type == other.type and self.sub_type == other.sub_type
        return False

    def __str__(self) -> str:
        """Return the weighted media range as a string."""
        return f"{self.type}/{self.sub_type};q={self.q}"

    def media_range(self) -> str:
        """Return the media range."""
        return f"{self.type}/{self.sub_type}"


async def prepare_weighted_media_ranges(
    accept_weighted_media_ranges: List[str],
) -> List[str]:
    """Prepare the accept weighted media ranges and sort on q-parameter."""
    logging.debug(
        f"Preparing accept weighted media ranges: {accept_weighted_media_ranges}"
    )
    # Assign q-parameter:
    accept_weighted_media_ranges_sorted: List[WeightedMediaRange] = []

    for accept_weighted_media_range in accept_weighted_media_ranges:
        weighted_media_range_split = accept_weighted_media_range.split(";")
        # Instantiate weighted media range:
        try:
            weighted_media_range = WeightedMediaRange(weighted_media_range_split[0])
            logging.debug(
                f"Assigning q-parameter for weighted media range: {accept_weighted_media_range}"
            )
            # If q-parameter is present, assign it:
            for weighted_media_range_part in weighted_media_range_split[1:]:
                if weighted_media_range_part.startswith("q="):
                    weighted_media_range.q = float(
                        # RFC specifies only 3 decimals may be used in q value.
                        # Must strip additional decimals so that q bonus from specificity
                        # results in correct sorting.
                        weighted_media_range_part.split("=")[1][0:5]
                    )

            accept_weighted_media_ranges_sorted.append(weighted_media_range)
        except InvalidMediaRangeError:
            logging.debug(
                "Ignoring invalid weighted media range: %s", accept_weighted_media_range
            )
            pass  # ignore invalid media range

    # Adjust q-parameters with regard to specificity:
    # Highest q-parameter is the most specific:
    for weighted_media_range in accept_weighted_media_ranges_sorted:
        logging.debug(
            f"Ajusting q-parameter for weighted media range: {weighted_media_range}"
        )
        if weighted_media_range.type == "*":
            pass
        elif weighted_media_range.sub_type == "*":
            weighted_media_range.q = weighted_media_range.q + 0.0001
        else:
            weighted_media_range.q = weighted_media_range.q + 0.0002

    # Sort on q-parameter and return list of weighted media ranges:
    accept_weighted_media_ranges_sorted.sort(key=lambda x: x.q, reverse=True)
    logging.debug(
        f"Accept weighted media ranges sorted: {', '.join(str(p) for p in accept_weighted_media_ranges_sorted)}"  # noqa: B950
    )
    return [
        weighted_media_range.media_range()
        for weighted_media_range in accept_weighted_media_ranges_sorted
    ]


async def decide_content_type(accept_weighted_media_ranges: List[str]) -> Optional[str]:
    """Decide the content type of the response."""
    logging.debug("Deciding content type")
    content_type = None
    accept_weighted_media_ranges_sorted = await prepare_weighted_media_ranges(
        accept_weighted_media_ranges
    )
    for weighted_media_range in accept_weighted_media_ranges_sorted:
        logging.debug(f"Checking weighted media range: {weighted_media_range}")
        if weighted_media_range in SUPPORTED_CONTENT_TYPES:
            content_type = weighted_media_range
            break
        elif weighted_media_range == "*/*":
            content_type = DEFAULT_CONTENT_TYPE["text"]
            break
        else:
            # Assumes valid mimetypes from `prepare_mime_types`
            media_range_type, media_range_subtype = weighted_media_range.split("/")
            if media_range_subtype == "*" and media_range_type in DEFAULT_CONTENT_TYPE:
                content_type = DEFAULT_CONTENT_TYPE[media_range_type]
                break
            else:
                content_type = None
    return content_type
