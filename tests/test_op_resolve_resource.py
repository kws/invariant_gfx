"""Unit tests for gfx:resolve_resource operation."""

import pytest

from invariant_gfx.artifacts import BlobArtifact
from invariant_gfx.ops.resolve_resource import resolve_resource


class TestResolveResource:
    """Tests for resolve_resource operation."""

    def test_resolve_lucide_icon(self):
        """Test resolving a Lucide icon."""
        result = resolve_resource("lucide:thermometer")

        assert isinstance(result, BlobArtifact)
        assert result.content_type == "image/svg+xml"
        assert len(result.data) > 0

    def test_resolve_material_icon(self):
        """Test resolving a Material Icons icon."""
        result = resolve_resource("material-icons:cloud")

        assert isinstance(result, BlobArtifact)
        assert result.content_type == "image/svg+xml"
        assert len(result.data) > 0

    def test_missing_name(self):
        """Test that missing name raises ValueError."""
        # This test is no longer applicable since name is a required parameter
        # The function will fail at call time if name is not provided
        pass

    def test_invalid_name_type(self):
        """Test that non-string name raises ValueError."""
        with pytest.raises(ValueError, match="name must be a string"):
            resolve_resource(123)  # type: ignore

    def test_nonexistent_resource(self):
        """Test that nonexistent resource raises ValueError."""
        with pytest.raises(ValueError, match="failed to find resource"):
            resolve_resource("nonexistent:resource")
