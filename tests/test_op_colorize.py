"""Unit tests for gfx:colorize operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.colorize import colorize


class TestColorize:
    """Tests for colorize operation."""

    def test_colorize_sets_rgb_preserves_alpha_shape(self):
        """Alpha-only mask with full color: output RGB is color, alpha unchanged."""
        # Source: RGB zeroed (e.g. from extract_alpha), alpha 255
        source = Image.new("RGBA", (6, 6), (0, 0, 0, 255))
        source = ImageArtifact(source)
        color = (100, 150, 200, 255)

        result = colorize(image=source, color=color)

        assert isinstance(result, ImageArtifact)
        assert result.width == 6 and result.height == 6
        assert result.image.getpixel((0, 0)) == (100, 150, 200, 255)

    def test_colorize_multiplies_alpha(self):
        """Output alpha = (source_alpha * color_alpha) / 255."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (50, 50, 50, 200)))
        color = (0, 0, 0, 128)  # color alpha 128

        result = colorize(image=source, color=color)

        # (200 * 128) // 255 = 100
        assert result.image.getpixel((5, 5)) == (0, 0, 0, 100)

    def test_dimensions_unchanged(self):
        """Output size equals input size."""
        source = ImageArtifact(Image.new("RGBA", (12, 8), (0, 0, 0, 255)))
        result = colorize(image=source, color=(1, 2, 3, 255))
        assert result.width == 12 and result.height == 8

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            colorize(image="not an image", color=(0, 0, 0, 255))  # type: ignore[arg-type]

    def test_invalid_color_not_tuple(self):
        """Color not a 4-tuple raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="color must be a tuple/list"):
            colorize(image=source, color=(0, 0, 0))  # type: ignore[arg-type]

    def test_invalid_color_out_of_range(self):
        """Color channel > 255 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="0-255"):
            colorize(image=source, color=(0, 0, 0, 256))  # type: ignore[arg-type]
