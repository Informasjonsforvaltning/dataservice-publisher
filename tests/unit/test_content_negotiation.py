"""Unit test cases for the catalogs route."""
from typing import List

import pytest

from dataservice_publisher.utils import decide_content_type


@pytest.mark.unit
async def test_content_negotiation() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["text/turtle", "application/ld+json"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "text/turtle" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be text/turtle."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_2() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["application/ld+json", "text/turtle"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/ld+json" == content_type
    ), f"For '{accept_weighted_media_ranges}', content-Type in response-header should be application/ld+json."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_3() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["not/acceptable", "*/*"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "text/turtle" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be text/turtle."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_4() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["text/plain", "*/*"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "text/turtle" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be text/turtle."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_5() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["*/*", "text/plain"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "text/turtle" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be text/turtle."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_6() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = [
        "application/json",
        "application/*",
        "*/*",
    ]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/rdf+xml" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be application/rdf+xml."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_7() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = [
        "*/*;q=0.8",
        "text/plain",
        "application/signed-exchange;q=0.9",
        "application/ld+json",
    ]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/ld+json" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be application/ld+json."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_8() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = [
        "*/*;q=0.8;v=b3",
        "text/plain",
        "application/signed-exchange;v=b3;q=0.9",
        "application/ld+json",
    ]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/ld+json" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be application/ld+json."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_9() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["application/ld+json;v=b3", "*/*"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/ld+json" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be application/ld+json."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_10() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["*/*", "text/*", "application/ld+json"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/ld+json" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be application/ld+json."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_11() -> None:
    """Should return 200 and correct content-type."""
    accept_weighted_media_ranges: List[str] = ["application/*", "text/turtle;q=0.2"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert (
        "application/rdf+xml" == content_type
    ), f"For header-value '{accept_weighted_media_ranges}', content-Type in response-header should be application/rdf+xml."  # noqa: B950


@pytest.mark.unit
async def test_content_negotiation_12() -> None:
    """Should return None."""
    accept_weighted_media_ranges: List[str] = ["text/"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert content_type is None, f"'{accept_weighted_media_ranges}' failed"


@pytest.mark.unit
async def test_content_negotiation_13() -> None:
    """Should return None."""
    accept_weighted_media_ranges: List[str] = ["text"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert content_type is None, f"'{accept_weighted_media_ranges}' failed"


@pytest.mark.unit
async def test_content_negotiation_14() -> None:
    """Should return None."""
    accept_weighted_media_ranges: List[str] = ["audio/*"]
    content_type = await decide_content_type(accept_weighted_media_ranges)
    assert content_type is None, f"'{accept_weighted_media_ranges}' failed"
