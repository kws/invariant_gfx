"""Unit tests for gfx:threshold_alpha operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.threshold_alpha import threshold_alpha


class TestThresholdAlpha:
    """Tests for threshold_alpha operation."""

    def test_alpha_above_threshold_becomes_255(self):
        """Alpha values >= t become 255."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 150, 200, 200)))

        result = threshold_alpha(image=source, t=128)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        assert result.image.getpixel((5, 5)) == (100, 150, 200, 255)

    def test_alpha_below_threshold_becomes_0(self):
        """Alpha values < t become 0."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (100, 150, 200, 100)))

        result = threshold_alpha(image=source, t=128)

        assert result.image.getpixel((5, 5)) == (100, 150, 200, 0)

    def test_alpha_at_threshold(self):
        """Alpha == t becomes 255 (spec: >= t)."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 128)))

        result = threshold_alpha(image=source, t=128)

        assert result.image.getpixel((0, 0)) == (0, 0, 0, 255)

    def test_dimensions_unchanged(self):
        """Output width and height equal input dimensions."""
        source = ImageArtifact(Image.new("RGBA", (24, 32), (255, 0, 0, 200)))

        result = threshold_alpha(image=source, t=100)

        assert result.width == 24
        assert result.height == 32

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be ImageArtifact"):
            threshold_alpha(image="not an image", t=128)  # type: ignore[arg-type]

    def test_invalid_threshold_below_zero(self):
        """t < 0 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 128)))
        with pytest.raises(ValueError, match="t must be int in 0-255"):
            threshold_alpha(image=source, t=-1)

    def test_invalid_threshold_above_255(self):
        """t > 255 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 128)))
        with pytest.raises(ValueError, match="t must be int in 0-255"):
            threshold_alpha(image=source, t=256)
