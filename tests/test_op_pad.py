"""Unit tests for gfx:pad operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.pad import pad


class TestPad:
    """Tests for pad operation."""

    def test_pad_expands_canvas(self):
        """Output size is (width + left + right, height + top + bottom)."""
        source = ImageArtifact(Image.new("RGBA", (10, 8), (0, 0, 0, 255)))

        result = pad(image=source, left=2, top=1, right=3, bottom=1)

        assert result.width == 15
        assert result.height == 10

    def test_pad_places_image_at_left_top(self):
        """Original image is at (left, top); padding area is transparent."""
        source = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        source.putpixel((0, 0), (255, 0, 0, 255))
        source = ImageArtifact(source)

        result = pad(image=source, left=2, top=1, right=1, bottom=1)

        assert result.image.getpixel((2, 1)) == (255, 0, 0, 255)
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 0)
        assert result.image.getpixel((6, 4)) == (0, 0, 0, 0)

    def test_pad_zero_unchanged(self):
        """left=top=right=bottom=0 -> same size, same content at (0,0)."""
        source = Image.new("RGBA", (6, 6), (50, 100, 150, 255))
        source.putpixel((0, 0), (1, 2, 3, 255))
        source = ImageArtifact(source)

        result = pad(image=source, left=0, top=0, right=0, bottom=0)

        assert result.width == 6 and result.height == 6
        assert result.image.getpixel((0, 0)) == (1, 2, 3, 255)

    def test_pad_negative_raises(self):
        """Negative padding raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="non-negative"):
            pad(image=source, left=0, top=0, right=-1, bottom=0)

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            pad(image="not an image", left=0, top=0, right=0, bottom=0)  # type: ignore[arg-type]

    def test_invalid_left_type(self):
        """left not int raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="left must be int"):
            pad(image=source, left=1.5, top=0, right=0, bottom=0)  # type: ignore[arg-type]
