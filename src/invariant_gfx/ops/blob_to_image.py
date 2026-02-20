"""gfx:blob_to_image operation - parses raw binary data into ImageArtifact."""

from io import BytesIO

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def blob_to_image(blob: BlobArtifact) -> ICacheable:
    """Parse raw binary data (PNG, JPEG, WEBP) into ImageArtifact.

    Args:
        blob: BlobArtifact (the blob to parse)

    Returns:
        ImageArtifact with decoded image (RGBA mode).

    Raises:
        ValueError: If blob is not a BlobArtifact or data cannot be parsed as an image.
    """
    if not isinstance(blob, BlobArtifact):
        raise ValueError(f"blob must be BlobArtifact, got {type(blob)}")

    # Parse the image from bytes
    try:
        image = Image.open(BytesIO(blob.data))
        # Convert to RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")
    except Exception as e:
        raise ValueError(
            f"gfx:blob_to_image failed to parse image data: {e}. "
            f"Content type: {blob.content_type}"
        ) from e

    return ImageArtifact(image)
