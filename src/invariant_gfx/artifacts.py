"""Artifact types for Invariant GFX."""

import hashlib
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from invariant.protocol import ICacheable
from PIL import Image


class ImageArtifact(ICacheable):
    """Universal visual primitive passed between nodes.

    Wraps a PIL.Image standardized to RGBA mode. Serialized as canonical PNG.
    """

    def __init__(self, image: Image.Image) -> None:
        """Initialize with a PIL Image.

        Args:
            image: PIL Image to wrap. Will be normalized to RGBA mode.
        """
        # Normalize to RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        self.image = image
        self._png_cache: bytes | None = None
        self._hash_cache: str | None = None

    @property
    def width(self) -> int:
        """Image width in pixels."""
        return self.image.width

    @property
    def height(self) -> int:
        """Image height in pixels."""
        return self.image.height

    def get_stable_hash(self) -> str:
        """SHA-256 hash of canonical PNG bytes."""
        if self._hash_cache is None:
            png_bytes = self._to_canonical_png()
            self._hash_cache = hashlib.sha256(png_bytes).hexdigest()
        return self._hash_cache

    def to_stream(self, stream: BinaryIO) -> None:
        """Serialize as canonical PNG."""
        png_bytes = self._to_canonical_png()
        stream.write(len(png_bytes).to_bytes(8, byteorder="big"))
        stream.write(png_bytes)

    def to_file(self, path: Path | str) -> None:
        """Write the image artifact as a canonical PNG file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self._to_canonical_png())

    @classmethod
    def from_stream(cls, stream: BinaryIO) -> "ImageArtifact":
        """Deserialize from canonical PNG."""
        length = int.from_bytes(stream.read(8), byteorder="big")
        png_bytes = stream.read(length)
        image = Image.open(BytesIO(png_bytes))
        return cls(image.convert("RGBA"))

    def _to_canonical_png(self) -> bytes:
        """Convert to canonical PNG (level 1, no metadata)."""
        if self._png_cache is not None:
            return self._png_cache

        buffer = BytesIO()
        self.image.save(buffer, format="PNG", compress_level=1, optimize=False)
        self._png_cache = buffer.getvalue()
        return self._png_cache


class BlobArtifact(ICacheable):
    """Container for raw binary resources (SVG, PNG, TTF, etc.).

    Stores raw bytes with a content_type (MIME type) for identification.
    """

    def __init__(self, data: bytes, content_type: str) -> None:
        """Initialize with binary data and content type.

        Args:
            data: Raw binary data.
            content_type: MIME type (e.g., "image/svg+xml", "font/ttf").
        """
        self.data = data
        self.content_type = content_type

    def get_stable_hash(self) -> str:
        """SHA-256 hash of raw bytes."""
        return hashlib.sha256(self.data).hexdigest()

    def to_stream(self, stream: BinaryIO) -> None:
        """Serialize content type and data with 8-byte length prefixes."""
        content_type_bytes = self.content_type.encode("utf-8")
        stream.write(len(content_type_bytes).to_bytes(8, byteorder="big"))
        stream.write(content_type_bytes)
        stream.write(len(self.data).to_bytes(8, byteorder="big"))
        stream.write(self.data)

    def to_file(self, path: Path | str) -> None:
        """Write the blob payload bytes to a file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(self.data)

    @classmethod
    def from_stream(cls, stream: BinaryIO) -> "BlobArtifact":
        """Deserialize from stream."""
        content_type_len = int.from_bytes(stream.read(8), byteorder="big")
        content_type = stream.read(content_type_len).decode("utf-8")
        data_len = int.from_bytes(stream.read(8), byteorder="big")
        data = stream.read(data_len)
        return cls(data, content_type)
