"""gfx:create_solid operation - generates a solid color canvas."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def create_solid(
    size: tuple[Decimal | int | str, Decimal | int | str],
    color: tuple[int, int, int, int],
) -> ICacheable:
    """Generate a solid color canvas.

    Args:
        size: Tuple[Decimal | int | str, Decimal | int | str] (width, height)
        color: Tuple[int, int, int, int] (RGBA, 0-255 per channel)

    Returns:
        ImageArtifact with the solid color canvas (RGBA mode).

    Raises:
        ValueError: If size or color values are invalid.
    """
    # Validate and convert size
    if not isinstance(size, (tuple, list)) or len(size) != 2:
        raise ValueError(f"size must be a tuple/list of 2 values, got {type(size)}")

    width_val = size[0]
    height_val = size[1]

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

    # Validate and convert color
    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )

    r, g, b, a = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b, a)):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    # Create solid color image
    image = Image.new("RGBA", (width, height), (r, g, b, a))

    return ImageArtifact(image)
