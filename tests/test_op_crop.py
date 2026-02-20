"""Unit tests for gfx:crop operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.crop import crop


class TestCrop:
    """Tests for crop operation."""

    def test_crop_shrinks_canvas(self):
        """Output size is (width - left - right, height - top - bottom)."""
        source = ImageArtifact(Image.new("RGBA", (10, 8), (0, 0, 0, 255)))

        result = crop(image=source, left=1, top=0, right=2, bottom=1)

        assert result.width == 7
        assert result.height == 7

    def test_crop_region_content(self):
        """Cropped region contains correct pixels; (2,1) in source becomes (1,1) in result."""
        source = Image.new("RGBA", (4, 4), (0, 0, 0, 0))
        source.putpixel((2, 1), (255, 0, 0, 255))
        source = ImageArtifact(source)

        result = crop(image=source, left=1, top=0, right=1, bottom=1)

        assert result.width == 2 and result.height == 3
        assert result.image.getpixel((1, 1)) == (255, 0, 0, 255)

    def test_crop_zero_unchanged(self):
        """left=top=right=bottom=0 -> same size, same content at (0,0)."""
        source = Image.new("RGBA", (6, 6), (50, 100, 150, 255))
        source.putpixel((0, 0), (1, 2, 3, 255))
        source = ImageArtifact(source)

        result = crop(image=source, left=0, top=0, right=0, bottom=0)

        assert result.width == 6 and result.height == 6
        assert result.image.getpixel((0, 0)) == (1, 2, 3, 255)

    def test_crop_negative_inset_raises(self):
        """Negative inset raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="non-negative"):
            crop(image=source, left=0, top=0, right=-1, bottom=0)

    def test_crop_invalid_dimensions_raises(self):
        """left+right >= width or top+bottom >= height raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="left \\+ right must be less than width"):
            crop(image=source, left=2, top=0, right=2, bottom=0)
        with pytest.raises(ValueError, match="top \\+ bottom must be less than height"):
            crop(image=source, left=0, top=2, right=0, bottom=2)

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            crop(image="not an image", left=0, top=0, right=0, bottom=0)  # type: ignore[arg-type]

    def test_invalid_left_type(self):
        """left not int raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (4, 4), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="left must be int"):
            crop(image=source, left=1.5, top=0, right=0, bottom=0)  # type: ignore[arg-type]
