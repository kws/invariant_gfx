"""gfx:resize operation - scales an ImageArtifact to target dimensions."""

from decimal import Decimal
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def resize(manifest: dict[str, Any]) -> ICacheable:
    """Scale an ImageArtifact to target dimensions.

    Args:
        manifest: Must contain:
            - 'image': ImageArtifact (the image to resize)
            - 'width': Decimal (target width)
            - 'height': Decimal (target height)

    Returns:
        ImageArtifact with resized image (RGBA mode).

    Raises:
        KeyError: If required keys are missing.
        ValueError: If width/height values are invalid.
    """
    if "image" not in manifest:
        raise KeyError("gfx:resize requires 'image' in manifest")
    if "width" not in manifest:
        raise KeyError("gfx:resize requires 'width' in manifest")
    if "height" not in manifest:
        raise KeyError("gfx:resize requires 'height' in manifest")

    image_artifact = manifest["image"]
    if not isinstance(image_artifact, ImageArtifact):
        raise ValueError(
            f"image must be ImageArtifact, got {type(image_artifact)}"
        )

    width_val = manifest["width"]
    height_val = manifest["height"]

    # Convert to int (handles Decimal, int, or string)
    if isinstance(width_val, Decimal):
        width = int(width_val)
    elif isinstance(width_val, (int, str)):
        width = int(width_val)
    else:
        raise ValueError(f"width must be Decimal, int, or str, got {type(width_val)}")

    if isinstance(height_val, Decimal):
        height = int(height_val)
    elif isinstance(height_val, (int, str)):
        height = int(height_val)
    else:
        raise ValueError(f"height must be Decimal, int, or str, got {type(height_val)}")

    if width <= 0 or height <= 0:
        raise ValueError(f"size must be positive, got {width}x{height}")

    # Resize the image
    resized_image = image_artifact.image.resize(
        (width, height), Image.Resampling.LANCZOS
    )

    return ImageArtifact(resized_image)
