"""Unit tests for gfx:invert_alpha operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.invert_alpha import invert_alpha


class TestInvertAlpha:
    """Tests for invert_alpha operation."""

    def test_inverts_alpha_values(self):
        """Alpha 180 becomes 75 (255 - 180); RGB unchanged."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 150, 200, 180)))

        result = invert_alpha(image=source)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        assert result.image.getpixel((5, 5)) == (100, 150, 200, 75)

    def test_dimensions_unchanged(self):
        """Output width and height equal input dimensions."""
        source = ImageArtifact(Image.new("RGBA", (24, 32), (255, 0, 0, 128)))

        result = invert_alpha(image=source)

        assert result.width == 24
        assert result.height == 32

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            invert_alpha(image="not an image")  # type: ignore[arg-type]

    def test_alpha_0_becomes_255(self):
        """Alpha 0 inverts to 255."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (50, 100, 150, 0)))

        result = invert_alpha(image=source)

        assert result.image.getpixel((0, 0)) == (50, 100, 150, 255)

    def test_alpha_255_becomes_0(self):
        """Alpha 255 inverts to 0."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 255)))

        result = invert_alpha(image=source)

        assert result.image.getpixel((0, 0)) == (0, 0, 0, 0)
