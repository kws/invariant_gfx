"""gfx:resize operation - scales an ImageArtifact to target dimensions."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def resize(
    image: ImageArtifact,
    width: Decimal | int | str,
    height: Decimal | int | str,
) -> ICacheable:
    """Scale an ImageArtifact to target dimensions.

    Args:
        image: ImageArtifact (the image to resize)
        width: Decimal | int | str (target width)
        height: Decimal | int | str (target height)

    Returns:
        ImageArtifact with resized image (RGBA mode).

    Raises:
        ValueError: If image is not an ImageArtifact or width/height values are invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    # Convert to int (handles Decimal, int, or string)
    if isinstance(width, Decimal):
        width_int = int(width)
    elif isinstance(width, (int, str)):
        width_int = int(width)
    else:
        raise ValueError(f"width must be Decimal, int, or str, got {type(width)}")

    if isinstance(height, Decimal):
        height_int = int(height)
    elif isinstance(height, (int, str)):
        height_int = int(height)
    else:
        raise ValueError(f"height must be Decimal, int, or str, got {type(height)}")

    if width_int <= 0 or height_int <= 0:
        raise ValueError(f"size must be positive, got {width_int}x{height_int}")

    # Resize the image
    resized_image = image.image.resize(
        (width_int, height_int), Image.Resampling.LANCZOS
    )

    return ImageArtifact(resized_image)
