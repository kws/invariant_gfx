"""Pytest configuration and fixtures."""

import pytest

from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore


TEST_FONT_FAMILY = "Inter"


@pytest.fixture
def registry():
    """Create a fresh OpRegistry instance."""
    registry = OpRegistry()
    registry.clear()
    return registry


@pytest.fixture
def store():
    """Create a fresh MemoryStore instance."""
    return MemoryStore()


@pytest.fixture(scope="session")
def test_font_family() -> str:
    """Return a font family the test process can render with.

    ``Inter`` is provided by the ``justmytype-western-core`` package, which is
    listed under both ``[project.optional-dependencies].fonts`` and the dev
    dependency group. If neither is installed the tests skip with a clear hint.
    """
    from justmytype import FontRegistry

    if FontRegistry().find_font(TEST_FONT_FAMILY) is None:
        pytest.skip(
            f"Font {TEST_FONT_FAMILY!r} not available; "
            "install 'invariant-gfx[fonts]' or run 'uv sync --all-groups'."
        )
    return TEST_FONT_FAMILY
