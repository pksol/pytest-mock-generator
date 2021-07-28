# type: ignore[attr-defined]
"""A pytest fixture wrapper for https://pypi.org/project/mock-generator"""

import sys

import mock_autogen
import pytest

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()


@pytest.fixture(scope="session")
def mg():
    """Mock generator fixture to provide mocking help."""
    return mock_autogen
