"""Unit tests for ImageArtifact and BlobArtifact."""

from io import BytesIO

from PIL import Image

from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


class TestImageArtifact:
    """Tests for ImageArtifact."""

    def test_rgba_normalization(self):
        """Test that images are normalized to RGBA mode."""
        # Create RGB image
        rgb_image = Image.new("RGB", (10, 10), (255, 0, 0))
        artifact = ImageArtifact(rgb_image)

        assert artifact.image.mode == "RGBA"
        assert artifact.width == 10
        assert artifact.height == 10

    def test_rgba_preserved(self):
        """Test that RGBA images remain RGBA."""
        rgba_image = Image.new("RGBA", (20, 30), (255, 128, 64, 200))
        artifact = ImageArtifact(rgba_image)

        assert artifact.image.mode == "RGBA"
        assert artifact.width == 20
        assert artifact.height == 30

    def test_hash_stability(self):
        """Test that identical images produce identical hashes."""
        image1 = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        image2 = Image.new("RGBA", (10, 10), (255, 0, 0, 255))

        artifact1 = ImageArtifact(image1)
        artifact2 = ImageArtifact(image2)

        assert artifact1.get_stable_hash() == artifact2.get_stable_hash()

    def test_hash_different_images(self):
        """Test that different images produce different hashes."""
        image1 = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        image2 = Image.new("RGBA", (10, 10), (0, 255, 0, 255))

        artifact1 = ImageArtifact(image1)
        artifact2 = ImageArtifact(image2)

        assert artifact1.get_stable_hash() != artifact2.get_stable_hash()

    def test_serialization_round_trip(self):
        """Test that serialization and deserialization preserves the image."""
        original_image = Image.new("RGBA", (15, 25), (128, 64, 32, 200))
        artifact = ImageArtifact(original_image)

        # Serialize
        stream = BytesIO()
        artifact.to_stream(stream)
        stream.seek(0)

        # Deserialize
        restored = ImageArtifact.from_stream(stream)

        assert restored.width == 15
        assert restored.height == 25
        assert restored.image.mode == "RGBA"

        # Check pixel data
        assert restored.image.getpixel((0, 0)) == (128, 64, 32, 200)

    def test_hash_after_serialization(self):
        """Test that hash is stable across serialization."""
        image = Image.new("RGBA", (10, 10), (255, 128, 64, 255))
        artifact1 = ImageArtifact(image)
        original_hash = artifact1.get_stable_hash()

        # Serialize and deserialize
        stream = BytesIO()
        artifact1.to_stream(stream)
        stream.seek(0)
        artifact2 = ImageArtifact.from_stream(stream)

        assert artifact2.get_stable_hash() == original_hash

    def test_canonical_png_is_cached(self):
        """Test that repeated PNG serialization reuses cached bytes."""
        image = Image.new("RGBA", (10, 10), (255, 128, 64, 255))
        artifact = ImageArtifact(image)

        first_png = artifact._to_canonical_png()
        second_png = artifact._to_canonical_png()

        assert first_png is second_png

    def test_hash_uses_cached_png(self):
        """Test that hashing and serialization share the cached PNG bytes."""
        image = Image.new("RGBA", (10, 10), (255, 128, 64, 255))
        artifact = ImageArtifact(image)

        original_png = artifact._to_canonical_png()
        artifact.get_stable_hash()

        stream = BytesIO()
        artifact.to_stream(stream)
        stream.seek(0)
        length = int.from_bytes(stream.read(8), byteorder="big")
        serialized_png = stream.read(length)

        assert serialized_png == original_png
        assert artifact._to_canonical_png() is original_png


class TestBlobArtifact:
    """Tests for BlobArtifact."""

    def test_creation(self):
        """Test basic creation."""
        data = b"test data"
        artifact = BlobArtifact(data, "text/plain")

        assert artifact.data == data
        assert artifact.content_type == "text/plain"

    def test_hash_stability(self):
        """Test that identical blobs produce identical hashes."""
        data = b"identical data"
        artifact1 = BlobArtifact(data, "text/plain")
        artifact2 = BlobArtifact(data, "text/plain")

        assert artifact1.get_stable_hash() == artifact2.get_stable_hash()

    def test_hash_different_data(self):
        """Test that different data produces different hashes."""
        artifact1 = BlobArtifact(b"data1", "text/plain")
        artifact2 = BlobArtifact(b"data2", "text/plain")

        assert artifact1.get_stable_hash() != artifact2.get_stable_hash()

    def test_serialization_round_trip(self):
        """Test that serialization and deserialization preserves the blob."""
        original_data = b"test binary data \x00\x01\x02"
        artifact = BlobArtifact(original_data, "application/octet-stream")

        # Serialize
        stream = BytesIO()
        artifact.to_stream(stream)
        stream.seek(0)

        # Deserialize
        restored = BlobArtifact.from_stream(stream)

        assert restored.data == original_data
        assert restored.content_type == "application/octet-stream"

    def test_hash_after_serialization(self):
        """Test that hash is stable across serialization."""
        data = b"test data for hashing"
        artifact1 = BlobArtifact(data, "text/plain")
        original_hash = artifact1.get_stable_hash()

        # Serialize and deserialize
        stream = BytesIO()
        artifact1.to_stream(stream)
        stream.seek(0)
        artifact2 = BlobArtifact.from_stream(stream)

        assert artifact2.get_stable_hash() == original_hash
