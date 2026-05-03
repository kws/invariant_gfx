"""Unit tests for gfx:resolve_color operation."""

import pytest
from invariant_gfx.ops.resolve_color import resolve_color


class TestResolveColor:
    """Tests for resolve_color operation."""

    def test_resolve_hex_rgb(self):
        """Test resolving a six-digit hex color."""
        assert resolve_color("#FF0000") == (255, 0, 0, 255)

    def test_resolve_hex_rgba(self):
        """Test resolving an eight-digit hex color."""
        assert resolve_color("#FF000080") == (255, 0, 0, 128)

    def test_resolve_named_color(self):
        """Test resolving a named CSS color."""
        assert resolve_color("red") == (255, 0, 0, 255)

    def test_resolve_transparent(self):
        """Test resolving transparent."""
        assert resolve_color("transparent") == (0, 0, 0, 0)

    def test_passthrough_rgb_tuple(self):
        """Test RGB tuple input is normalized to RGBA."""
        assert resolve_color((1, 2, 3)) == (1, 2, 3, 255)

    def test_passthrough_rgba_list(self):
        """Test RGBA list input is normalized to tuple."""
        assert resolve_color([1, 2, 3, 4]) == (1, 2, 3, 4)

    def test_invalid_string_raises_value_error(self):
        """Test invalid color string raises ValueError."""
        with pytest.raises(ValueError):
            resolve_color("not-a-real-color")

    def test_invalid_channel_count_raises_value_error(self):
        """Test invalid tuple length raises ValueError."""
        with pytest.raises(ValueError):
            resolve_color((1, 2))

    def test_invalid_channel_value_raises_value_error(self):
        """Test invalid tuple channels raise ValueError."""
        with pytest.raises(ValueError):
            resolve_color((1, 2, 999))
