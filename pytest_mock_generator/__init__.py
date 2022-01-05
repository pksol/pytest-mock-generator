# type: ignore[attr-defined]
"""A pytest fixture wrapper for https://pypi.org/project/mock-generator"""

import sys
from functools import partial

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


class PytestMockGenerator:
    """
    A simplified version of the mock_autogen library.
    """

    generate_uut_mocks = mock_autogen.generate_uut_mocks
    generate_asserts = mock_autogen.generate_asserts
    generate_uut_mocks_with_asserts = partial(
        mock_autogen.generate_uut_mocks_with_asserts,
        include_mock_autogen_import=False,
        mock_autogen_alias="mg",
    )


@pytest.fixture(scope="session")
def mg():
    """Mock generator fixture to provide mocking help."""
    return PytestMockGenerator
