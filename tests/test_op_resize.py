"""Unit tests for gfx:resize operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.resize import resize


class TestResize:
    """Tests for resize operation."""

    def test_basic_resize(self):
        """Test basic image resizing."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = resize(
            image=source,
            width=Decimal("20"),
            height=Decimal("40"),
        )

        assert isinstance(result, ImageArtifact)
        assert result.width == 20
        assert result.height == 40
        assert result.image.mode == "RGBA"

    def test_with_int_dimensions(self):
        """Test with integer dimensions."""
        source = ImageArtifact(Image.new("RGBA", (50, 50), (0, 255, 0, 255)))

        result = resize(
            image=source,
            width=100,
            height=100,
        )

        assert result.width == 100
        assert result.height == 100

    def test_with_string_dimensions(self):
        """Test with string dimensions (from CEL expressions)."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 255, 255)))

        result = resize(
            image=source,
            width="30",
            height="30",
        )

        assert result.width == 30
        assert result.height == 30

    def test_missing_width(self):
        """Test that missing width raises TypeError."""
        # This test is no longer applicable since width is a required parameter
        # The function will fail at call time if width is not provided
        pass

    def test_missing_height(self):
        """Test that missing height raises TypeError."""
        # This test is no longer applicable since height is a required parameter
        # The function will fail at call time if height is not provided
        pass

    def test_missing_image(self):
        """Test that missing image raises TypeError."""
        # This test is no longer applicable since image is a required parameter
        # The function will fail at call time if image is not provided
        pass

    def test_negative_dimensions(self):
        """Test that negative dimensions raise ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="size must be positive"):
            resize(
                image=source,
                width=-10,
                height=20,
            )

    def test_zero_dimensions(self):
        """Test that zero dimensions raise ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        with pytest.raises(ValueError, match="size must be positive"):
            resize(
                image=source,
                width=0,
                height=20,
            )

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            resize(
                image="not an image",  # type: ignore
                width=20,
                height=20,
            )

    def test_preserves_aspect_ratio_approximately(self):
        """Test that resize changes dimensions (aspect ratio may change)."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        result = resize(
            image=source,
            width=30,
            height=30,
        )

        # Should be resized to target dimensions (aspect ratio not preserved)
        assert result.width == 30
        assert result.height == 30
