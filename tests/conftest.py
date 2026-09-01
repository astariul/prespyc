"""pytest fixtures for the prespyc test suite. See `tests/support.py` for the helpers themselves."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.support import FIXTURES, SwfBuilder


@pytest.fixture(scope="session")
def fixtures_dir():
    """Root of the fixture tree."""
    return FIXTURES


@pytest.fixture
def swf_builder() -> Iterator[SwfBuilder]:
    """Builder for synthetic SWF files, cleaned up at the end of the test."""
    builder = SwfBuilder()
    yield builder
    builder.cleanup()
