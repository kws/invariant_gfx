"""Unit tests for gfx:gaussian_blur operation."""

from decimal import Decimal

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.gaussian_blur import gaussian_blur


class TestGaussianBlur:
    """Tests for gaussian_blur operation."""

    def test_blur_softens_image(self):
        """Blur changes at least one pixel; output is ImageArtifact, same size."""
        source = Image.new("RGBA", (8, 8), (100, 150, 200, 255))
        source.putpixel((4, 4), (255, 0, 0, 255))
        source = ImageArtifact(source)

        result = gaussian_blur(image=source, sigma=2)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        assert result.width == 8 and result.height == 8
        # Blur should change center pixel (was solid red)
        assert result.image.getpixel((4, 4)) != (255, 0, 0, 255)

    def test_dimensions_unchanged(self):
        """Output width and height equal input."""
        source = ImageArtifact(Image.new("RGBA", (24, 32), (0, 0, 0, 255)))

        result = gaussian_blur(image=source, sigma=1)

        assert result.width == 24
        assert result.height == 32

    def test_sigma_zero_no_blur(self):
        """sigma=0 gives radius=0; Pillow returns copy; same pixel as source."""
        source = ImageArtifact(Image.new("RGBA", (6, 6), (10, 20, 30, 180)))

        result = gaussian_blur(image=source, sigma=0)

        assert result.width == 6 and result.height == 6
        assert result.image.getpixel((3, 3)) == (10, 20, 30, 180)

    def test_invalid_image_type(self):
        """Non-ImageArtifact raises ValueError."""
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            gaussian_blur(image="not an image", sigma=1)  # type: ignore[arg-type]

    def test_negative_sigma_raises(self):
        """sigma < 0 raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="non-negative"):
            gaussian_blur(image=source, sigma=Decimal("-0.5"))

    def test_sigma_decimal_accepted(self):
        """sigma=Decimal('1.5') runs and returns same-size ImageArtifact."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (50, 50, 50, 255)))

        result = gaussian_blur(image=source, sigma=Decimal("1.5"))

        assert isinstance(result, ImageArtifact)
        assert result.width == 10 and result.height == 10
