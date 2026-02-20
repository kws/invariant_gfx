"""Unit tests for gfx:dilate operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.dilate import dilate


class TestDilate:
    """Tests for dilate operation."""

    def test_dilate_expands_alpha(self):
        """Alpha shape expands by radius; a formerly 0 pixel near edge becomes 255."""
        # 10x10 image: 4x4 opaque center (pixels 3-6), rest transparent
        source = Image.new("RGBA", (10, 10), (100, 150, 200, 0))
        for x in range(3, 7):
            for y in range(3, 7):
                source.putpixel((x, y), (100, 150, 200, 255))
        source = ImageArtifact(source)

        result = dilate(image=source, radius=1)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        # Pixel (2, 3) was 0, adjacent to (3,3) which is 255; after 3x3 max it becomes 255
        assert result.image.getpixel((2, 3)) == (100, 150, 200, 255)

    def test_dimensions_unchanged(self):
        """Output width and height equal input."""
        source = ImageArtifact(Image.new("RGBA", (24, 32), (0, 0, 0, 255)))

        result = dilate(image=source, radius=2)

        assert result.width == 24
        assert result.height == 32

    def test_rgb_preserved(self):
        """RGB channels unchanged after dilate."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (50, 100, 150, 255)))

        result = dilate(image=source, radius=1)

        assert result.image.getpixel((4, 4)) == (50, 100, 150, 255)

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            dilate(image="not an image", radius=1)  # type: ignore[arg-type]

    def test_negative_radius_raises(self):
        """radius < 0 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="non-negative int"):
            dilate(image=source, radius=-1)

    def test_radius_zero(self):
        """radius 0 (kernel size 1) leaves alpha unchanged."""
        source = ImageArtifact(Image.new("RGBA", (6, 6), (10, 20, 30, 180)))

        result = dilate(image=source, radius=0)

        assert result.image.getpixel((3, 3)) == (10, 20, 30, 180)
