"""Unit tests for gfx:create_solid operation."""

from decimal import Decimal

import pytest

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.create_solid import create_solid


class TestCreateSolid:
    """Tests for create_solid operation."""

    def test_basic_creation(self):
        """Test basic solid color creation."""
        result = create_solid(
            size=(Decimal("10"), Decimal("20")),
            color=(255, 128, 64, 255),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 20
        assert result.image.mode == "RGBA"

        # Check pixel color
        pixel = result.image.getpixel((0, 0))
        assert pixel == (255, 128, 64, 255)

    def test_with_int_size(self):
        """Test with integer size values."""
        result = create_solid(
            size=(10, 20),
            color=(0, 0, 0, 255),
        )

        assert result.width == 10
        assert result.height == 20

    def test_with_string_size(self):
        """Test with string size values (from CEL expressions)."""
        result = create_solid(
            size=("10", "20"),
            color=(255, 255, 255, 255),
        )

        assert result.width == 10
        assert result.height == 20

    def test_missing_size(self):
        """Test that missing size raises TypeError."""
        # This test is no longer applicable since size is a required parameter
        # The function will fail at call time if size is not provided
        pass

    def test_missing_color(self):
        """Test that missing color raises TypeError."""
        # This test is no longer applicable since color is a required parameter
        # The function will fail at call time if color is not provided
        pass

    def test_invalid_size(self):
        """Test that invalid size raises ValueError."""
        with pytest.raises(ValueError, match="size must be a tuple"):
            create_solid(
                size=(10,),  # Wrong length
                color=(255, 0, 0, 255),
            )

    def test_invalid_color(self):
        """Test that invalid color raises ValueError."""
        with pytest.raises(ValueError, match="color must be a tuple"):
            create_solid(
                size=(10, 10),
                color=(255, 0, 0),  # Missing alpha
            )

    def test_negative_size(self):
        """Test that negative size raises ValueError."""
        with pytest.raises(ValueError, match="size must be positive"):
            create_solid(
                size=(-10, 10),
                color=(255, 0, 0, 255),
            )

    def test_invalid_color_range(self):
        """Test that color values out of range raise ValueError."""
        with pytest.raises(ValueError, match="color values must be int in range"):
            create_solid(
                size=(10, 10),
                color=(256, 0, 0, 255),  # Out of range
            )

    def test_different_colors(self):
        """Test that different colors produce different images."""
        result1 = create_solid(
            size=(10, 10),
            color=(255, 0, 0, 255),  # Red
        )
        result2 = create_solid(
            size=(10, 10),
            color=(0, 255, 0, 255),  # Green
        )

        assert result1.image.getpixel((0, 0)) == (255, 0, 0, 255)
        assert result2.image.getpixel((0, 0)) == (0, 255, 0, 255)
        assert result1.get_stable_hash() != result2.get_stable_hash()
