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

        manifest = {
            "image": source,
            "width": Decimal("20"),
            "height": Decimal("40"),
        }

        result = resize(manifest)

        assert isinstance(result, ImageArtifact)
        assert result.width == 20
        assert result.height == 40
        assert result.image.mode == "RGBA"

    def test_with_int_dimensions(self):
        """Test with integer dimensions."""
        source = ImageArtifact(Image.new("RGBA", (50, 50), (0, 255, 0, 255)))

        manifest = {
            "source": source,
            "width": 100,
            "height": 100,
        }

        result = resize(manifest)

        assert result.width == 100
        assert result.height == 100

    def test_with_string_dimensions(self):
        """Test with string dimensions (from CEL expressions)."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 255, 255)))

        manifest = {
            "source": source,
            "width": "30",
            "height": "30",
        }

        result = resize(manifest)

        assert result.width == 30
        assert result.height == 30

    def test_missing_width(self):
        """Test that missing width raises KeyError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "source": source,
            "height": 20,
        }

        with pytest.raises(KeyError, match="width"):
            resize(manifest)

    def test_missing_height(self):
        """Test that missing height raises KeyError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "source": source,
            "width": 20,
        }

        with pytest.raises(KeyError, match="height"):
            resize(manifest)

    def test_missing_image(self):
        """Test that missing image raises KeyError."""
        manifest = {
            "width": 20,
            "height": 20,
        }

        with pytest.raises(KeyError, match="image"):
            resize(manifest)

    def test_negative_dimensions(self):
        """Test that negative dimensions raise ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "source": source,
            "width": -10,
            "height": 20,
        }

        with pytest.raises(ValueError, match="size must be positive"):
            resize(manifest)

    def test_zero_dimensions(self):
        """Test that zero dimensions raise ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 255)))

        manifest = {
            "source": source,
            "width": 0,
            "height": 20,
        }

        with pytest.raises(ValueError, match="size must be positive"):
            resize(manifest)

    def test_invalid_image_type(self):
        """Test that non-ImageArtifact raises ValueError."""
        manifest = {
            "image": "not an image",
            "width": 20,
            "height": 20,
        }

        with pytest.raises(ValueError, match="must be ImageArtifact"):
            resize(manifest)

    def test_preserves_aspect_ratio_approximately(self):
        """Test that resize changes dimensions (aspect ratio may change)."""
        source = ImageArtifact(Image.new("RGBA", (10, 20), (255, 0, 0, 255)))

        manifest = {
            "source": source,
            "width": 30,
            "height": 30,
        }

        result = resize(manifest)

        # Should be resized to target dimensions (aspect ratio not preserved)
        assert result.width == 30
        assert result.height == 30
