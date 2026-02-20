"""gfx:opacity operation - multiplies the alpha channel by a factor."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def opacity(
    image: ImageArtifact,
    factor: Decimal | int | str,
) -> ICacheable:
    """Multiply the alpha channel by a factor (0 to 1). RGB preserved.

    Args:
        image: ImageArtifact (source image).
        factor: Decimal | int | str (opacity multiplier, 0 to 1).

    Returns:
        ImageArtifact with RGB unchanged and alpha multiplied by factor.

    Raises:
        ValueError: If image is not an ImageArtifact or factor is invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    if isinstance(factor, Decimal):
        factor_float = float(factor)
    elif isinstance(factor, (int, str)):
        factor_float = float(factor)
    else:
        raise ValueError(f"factor must be Decimal, int, or str, got {type(factor)}")
    if factor_float < 0 or factor_float > 1:
        raise ValueError(f"factor must be in range 0 to 1, got {factor_float}")

    r, g, b, a = image.image.split()
    a_out = a.point(lambda x: int(x * factor_float), mode="L")
    out = Image.merge("RGBA", (r, g, b, a_out))
    return ImageArtifact(out)
