"""gfx:crop_region operation - crops a region by (x, y, width, height)."""

from decimal import Decimal

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def _to_int(value: Decimal | int | str) -> int:
    """Convert value to int for CEL compatibility."""
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, (int, str)):
        return int(value)
    raise ValueError(f"value must be Decimal, int, or str, got {type(value)}")


def crop_region(
    image: ImageArtifact,
    x: Decimal | int | str,
    y: Decimal | int | str,
    width: Decimal | int | str,
    height: Decimal | int | str,
) -> ICacheable:
    """Extract a rectangular region from an image.

    Args:
        image: ImageArtifact (source image).
        x: Left edge of region (pixels).
        y: Top edge of region (pixels).
        width: Width of region (pixels).
        height: Height of region (pixels).

    Returns:
        ImageArtifact with the extracted region.

    Raises:
        ValueError: If image is not an ImageArtifact, params are invalid,
            or region is out of bounds.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    x_int = _to_int(x)
    y_int = _to_int(y)
    w_int = _to_int(width)
    h_int = _to_int(height)

    if x_int < 0 or y_int < 0:
        raise ValueError(f"x and y must be non-negative, got x={x_int} y={y_int}")
    if w_int <= 0 or h_int <= 0:
        raise ValueError(f"width and height must be positive, got {w_int}x{h_int}")

    img_w = image.width
    img_h = image.height
    if x_int + w_int > img_w:
        raise ValueError(
            f"region x+width ({x_int}+{w_int}) exceeds image width ({img_w})"
        )
    if y_int + h_int > img_h:
        raise ValueError(
            f"region y+height ({y_int}+{h_int}) exceeds image height ({img_h})"
        )

    box = (x_int, y_int, x_int + w_int, y_int + h_int)
    cropped = image.image.crop(box)
    return ImageArtifact(cropped)
