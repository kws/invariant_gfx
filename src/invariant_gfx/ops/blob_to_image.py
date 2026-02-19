"""gfx:blob_to_image operation - parses raw binary data into ImageArtifact."""

from io import BytesIO
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def blob_to_image(manifest: dict[str, Any]) -> ICacheable:
    """Parse raw binary data (PNG, JPEG, WEBP) into ImageArtifact.

    Args:
        manifest: Must contain:
            - 'blob': BlobArtifact (the blob to parse)

    Returns:
        ImageArtifact with decoded image (RGBA mode).

    Raises:
        KeyError: If BlobArtifact is missing.
        ValueError: If blob data cannot be parsed as an image.
    """
    if "blob" not in manifest:
        raise KeyError("gfx:blob_to_image requires 'blob' in manifest")

    blob_artifact = manifest["blob"]
    if not isinstance(blob_artifact, BlobArtifact):
        raise ValueError(
            f"blob must be BlobArtifact, got {type(blob_artifact)}"
        )

    # Parse the image from bytes
    try:
        image = Image.open(BytesIO(blob_artifact.data))
        # Convert to RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")
    except Exception as e:
        raise ValueError(
            f"gfx:blob_to_image failed to parse image data: {e}. "
            f"Content type: {blob_artifact.content_type}"
        ) from e

    return ImageArtifact(image)
