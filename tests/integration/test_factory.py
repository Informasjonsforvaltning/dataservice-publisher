"""Unit test cases for the factory."""
import pytest

from dataservice_publisher import create_app


@pytest.mark.integration
def test_config() -> None:
    """Should return configuration if test config is passed."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing
