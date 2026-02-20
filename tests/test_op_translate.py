"""Unit tests for gfx:translate operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.translate import translate


class TestTranslate:
    """Tests for translate operation."""

    def test_translate_offset_moves_pixel(self):
        """Pixel that was at (0,0) is at (2,1) after dx=2, dy=1; (0,0) and (1,0) transparent."""
        source = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        source.putpixel((0, 0), (255, 0, 0, 255))
        source = ImageArtifact(source)

        result = translate(image=source, dx=2, dy=1)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        assert result.image.getpixel((2, 1)) == (255, 0, 0, 255)
        assert result.image.getpixel((0, 0)) == (0, 0, 0, 0)
        assert result.image.getpixel((1, 0)) == (0, 0, 0, 0)

    def test_translate_canvas_expanded(self):
        """Output size is (width + abs(dx), height + abs(dy)) for non-zero dx, dy."""
        source = ImageArtifact(Image.new("RGBA", (10, 8), (0, 0, 0, 255)))

        result = translate(image=source, dx=3, dy=2)

        assert result.width == 13
        assert result.height == 10

    def test_translate_zero_zero_unchanged(self):
        """dx=0, dy=0 -> same size, same pixel at (0,0)."""
        source = Image.new("RGBA", (6, 6), (50, 100, 150, 200))
        source.putpixel((0, 0), (1, 2, 3, 255))
        source = ImageArtifact(source)

        result = translate(image=source, dx=0, dy=0)

        assert result.width == 6 and result.height == 6
        assert result.image.getpixel((0, 0)) == (1, 2, 3, 255)

    def test_translate_negative_dx(self):
        """dx=-1, dy=0 -> paste at (0,0); pixel at (0,0) is source (0,0); right column transparent."""
        source = Image.new("RGBA", (3, 2), (0, 0, 0, 0))
        source.putpixel((0, 0), (10, 20, 30, 255))
        source = ImageArtifact(source)

        result = translate(image=source, dx=-1, dy=0)

        assert result.width == 4 and result.height == 2
        assert result.image.getpixel((0, 0)) == (10, 20, 30, 255)
        assert result.image.getpixel((3, 0)) == (0, 0, 0, 0)

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            translate(image="not an image", dx=0, dy=0)  # type: ignore[arg-type]

    def test_invalid_dx_type(self):
        """dx not int raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="dx must be int"):
            translate(image=source, dx=1.5, dy=0)  # type: ignore[arg-type]
