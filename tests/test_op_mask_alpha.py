"""Unit tests for gfx:mask_alpha operation."""

import pytest
from PIL import Image

from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops.mask_alpha import mask_alpha


class TestMaskAlpha:
    """Tests for mask_alpha operation."""

    def test_mask_alpha_multiplies_alpha(self):
        """Output alpha = (image_alpha * mask_alpha) / 255; RGB unchanged."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (255, 0, 0, 200)))
        mask = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 128)))

        result = mask_alpha(image=source, mask=mask)

        assert isinstance(result, ImageArtifact)
        assert result.image.mode == "RGBA"
        # (200 * 128) // 255 = 100
        assert result.image.getpixel((5, 5)) == (255, 0, 0, 100)

    def test_mask_alpha_full_mask(self):
        """Mask alpha 255 -> output alpha equals source alpha."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (0, 100, 200, 180)))
        mask = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 255)))

        result = mask_alpha(image=source, mask=mask)

        assert result.image.getpixel((0, 0)) == (0, 100, 200, 180)

    def test_mask_alpha_zero_mask(self):
        """Mask alpha 0 -> output alpha 0."""
        source = ImageArtifact(Image.new("RGBA", (8, 8), (50, 100, 150, 255)))
        mask = ImageArtifact(Image.new("RGBA", (8, 8), (0, 0, 0, 0)))

        result = mask_alpha(image=source, mask=mask)

        assert result.image.getpixel((0, 0)) == (50, 100, 150, 0)

    def test_dimensions_unchanged(self):
        """Output size equals source/mask size."""
        source = ImageArtifact(Image.new("RGBA", (24, 32), (0, 0, 0, 255)))
        mask = ImageArtifact(Image.new("RGBA", (24, 32), (0, 0, 0, 128)))

        result = mask_alpha(image=source, mask=mask)

        assert result.width == 24
        assert result.height == 32

    def test_invalid_image_type(self):
        """Non-ImageArtifact image raises ValueError."""
        mask = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="image must be ImageArtifact"):
            mask_alpha(image="not an image", mask=mask)  # type: ignore[arg-type]

    def test_invalid_mask_type(self):
        """Non-ImageArtifact mask raises ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="mask must be ImageArtifact"):
            mask_alpha(image=source, mask="not a mask")  # type: ignore[arg-type]

    def test_size_mismatch_raises(self):
        """Image and mask different sizes raise ValueError."""
        source = ImageArtifact(Image.new("RGBA", (10, 10), (0, 0, 0, 255)))
        mask = ImageArtifact(Image.new("RGBA", (20, 20), (0, 0, 0, 255)))
        with pytest.raises(ValueError, match="same dimensions"):
            mask_alpha(image=source, mask=mask)
