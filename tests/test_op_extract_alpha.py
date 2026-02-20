"""Unit tests for gfx:extract_alpha operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.extract_alpha import extract_alpha


class TestExtractAlpha:
    """Tests for extract_alpha operation."""

    def test_preserves_alpha_rgb_zeroed(self):
        """Alpha is preserved and RGB channels are zeroed."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 150, 200, 180)))

        result = extract_alpha(image=source)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        assert result.image.getpixel((5, 5)) == (0, 0, 0, 180)

    def test_dimensions_unchanged(self):
        """Output width and height equal input dimensions."""
        source = ImageArtifact(Image.new("RGBA", (24, 32), (255, 0, 0, 255)))

        result = extract_alpha(image=source)

        assert result.width == 24
        assert result.height == 32

    def test_semi_transparent_alpha_preserved(self):
        """Semi-transparent alpha value is preserved exactly."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (50, 100, 150, 100)))

        result = extract_alpha(image=source)

        assert result.image.getpixel((0, 0)) == (0, 0, 0, 100)

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            extract_alpha(image="not an image")  # type: ignore[arg-type]
