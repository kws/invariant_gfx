"""Unit tests for gfx:opacity operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.opacity import opacity


class TestOpacity:
    """Tests for opacity operation."""

    def test_opacity_reduces_alpha(self):
        """Alpha 200, factor 0.5 -> alpha 100."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 200)))
        result = opacity(image=source, factor=Decimal("0.5"))
        assert result.image.getpixel((5, 5)) == (255, 0, 0, 100)

    def test_opacity_zero(self):
        """Factor 0 -> alpha 0 everywhere."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (100, 150, 200, 255)))
        result = opacity(image=source, factor=0)
        assert result.image.getpixel((0, 0)) == (100, 150, 200, 0)

    def test_opacity_one_unchanged(self):
        """Factor 1 -> alpha unchanged."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (1, 2, 3, 180)))
        result = opacity(image=source, factor=1)
        assert result.image.getpixel((0, 0)) == (1, 2, 3, 180)

    def test_dimensions_unchanged(self):
        """Output size equals input size."""
        source = ImageArtifact(Image.new("RGBA", (12, 8), (0, 0, 0, 255)))
        result = opacity(image=source, factor=Decimal("0.5"))
        assert result.width == 12 and result.height == 8

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            opacity(image="not an image", factor=0.5)  # type: ignore[arg-type]

    def test_invalid_factor_negative_raises(self):
        """Factor < 0 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="0 to 1"):
            opacity(image=source, factor=Decimal("-0.1"))

    def test_invalid_factor_above_one_raises(self):
        """Factor > 1 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="0 to 1"):
            opacity(image=source, factor=Decimal("1.5"))

    def test_factor_decimal_accepted(self):
        """Decimal factor works."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 200)))
        result = opacity(image=source, factor=Decimal("0.5"))
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 100)
