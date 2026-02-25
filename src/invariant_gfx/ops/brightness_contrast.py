"""gfx:brightness_contrast operation - adjusts brightness and contrast levels."""

from decimal import Decimal

from PIL import ImageEnhance

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def _to_float(value: Decimal | int | str) -> float:
    """Convert value to float for PIL. Callers must pass Decimal, int, or str (not float)."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, str)):
        return float(value)
    raise ValueError(f"value must be Decimal, int, or str, got {type(value)}")


def brightness_contrast(
    image: ImageArtifact,
    brightness: Decimal | int | str = 1,
    contrast: Decimal | int | str = 1,
) -> ICacheable:
    """Adjust brightness and contrast of an image.

    Args:
        image: ImageArtifact (source image).
        brightness: Factor (1 = no change, 2 = twice as bright, 0.5 = half).
            Pass Decimal, int, or str — not Python float (strict numeric policy).
        contrast: Factor (1 = no change, 2 = more contrast, 0.5 = less).
            Pass Decimal, int, or str — not Python float (strict numeric policy).

    Returns:
        ImageArtifact with adjusted brightness and contrast.

    Raises:
        ValueError: If image is not an ImageArtifact or params are invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    brightness_float = _to_float(brightness)
    contrast_float = _to_float(contrast)

    out = image.image
    out = ImageEnhance.Brightness(out).enhance(brightness_float)
    out = ImageEnhance.Contrast(out).enhance(contrast_float)
    return ImageArtifact(out)
