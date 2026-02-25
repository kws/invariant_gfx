"""gfx:rotate operation - rotates an ImageArtifact by angle in degrees."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def _to_float(value: Decimal | int | str) -> float:
    """Convert value to float for PIL (canonical conversion for determinism)."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (int, str)):
        return float(value)
    raise ValueError(f"angle must be Decimal, int, or str, got {type(value)}")


def rotate(
    image: ImageArtifact,
    angle: Decimal | int | str,
    expand: bool = True,
) -> ICacheable:
    """Rotate an ImageArtifact by angle in degrees.

    Args:
        image: ImageArtifact (the image to rotate).
        angle: Rotation in degrees (positive = counter-clockwise).
        expand: If True (default), expand canvas so no content is cropped.
            If False, keep original size (crops corners).

    Returns:
        ImageArtifact with rotated image (RGBA mode).

    Raises:
        ValueError: If image is not an ImageArtifact or angle is invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    angle_float = _to_float(angle)

    rotated = image.image.rotate(
        angle_float,
        expand=expand,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )

    return ImageArtifact(rotated)
