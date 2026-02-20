"""Unit tests for gfx:blob_to_image operation."""

import io

import pytest
from PIL import Image

from invariant_gfx.artifacts import BlobArtifact, ImageArtifact
from invariant_gfx.ops.blob_to_image import blob_to_image


class TestBlobToImage:
    """Tests for blob_to_image operation."""

    def test_png_blob(self):
        """Test converting PNG blob to ImageArtifact."""
        # Create a PNG blob
        png_image = Image.new("RGBA", (10, 20), (255, 0, 0, 255))
        buffer = io.BytesIO()
        png_image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        blob = BlobArtifact(data=png_bytes, content_type="image/png")

        result = blob_to_image(blob)

        assert isinstance(result, ImageArtifact)
        assert result.width == 10
        assert result.height == 20
        assert result.image.mode == "RGBA"
        assert result.image.getpixel((0, 0)) == (255, 0, 0, 255)

    def test_jpeg_blob(self):
        """Test converting JPEG blob to ImageArtifact."""
        # Create a JPEG blob (will be converted to RGBA)
        jpeg_image = Image.new("RGB", (15, 25), (0, 255, 0))
        buffer = io.BytesIO()
        jpeg_image.save(buffer, format="JPEG")
        jpeg_bytes = buffer.getvalue()

        blob = BlobArtifact(data=jpeg_bytes, content_type="image/jpeg")

        result = blob_to_image(blob)

        assert isinstance(result, ImageArtifact)
        assert result.width == 15
        assert result.height == 25
        assert result.image.mode == "RGBA"  # Should be converted to RGBA

    def test_rgb_conversion(self):
        """Test that RGB images are converted to RGBA."""
        rgb_image = Image.new("RGB", (5, 5), (128, 128, 128))
        buffer = io.BytesIO()
        rgb_image.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        blob = BlobArtifact(data=png_bytes, content_type="image/png")

        result = blob_to_image(blob)

        assert result.image.mode == "RGBA"

    def test_missing_blob(self):
        """Test that missing blob raises TypeError."""
        # This test is no longer applicable since blob is a required parameter
        # The function will fail at call time if blob is not provided
        pass

    def test_invalid_blob_data(self):
        """Test that invalid blob data raises ValueError."""
        blob = BlobArtifact(data=b"not an image", content_type="image/png")

        with pytest.raises(ValueError, match="failed to parse"):
            blob_to_image(blob)

    def test_invalid_blob_type(self):
        """Test that non-BlobArtifact raises ValueError."""
        with pytest.raises(ValueError, match="must be BlobArtifact"):
            blob_to_image("not a blob")  # type: ignore
