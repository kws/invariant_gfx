"""gfx:gaussian_blur operation - applies Gaussian blur to an image."""

from decimal import ROUND_CEILING, Decimal

from PIL import ImageFilter

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def gaussian_blur(
    image: ImageArtifact,
    sigma: Decimal | int | str,
) -> ICacheable:
    """Apply Gaussian blur. Deterministic: radius = ceil(3 * sigma).

    Args:
        image: ImageArtifact (source image).
        sigma: Blur standard deviation (Decimal, int, or str). Non-negative.

    Returns:
        ImageArtifact with blurred image (all channels).

    Raises:
        ValueError: If image is not an ImageArtifact or sigma is invalid/negative.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    if isinstance(sigma, Decimal):
        sigma_dec = sigma
    elif isinstance(sigma, (int, str)):
        sigma_dec = Decimal(str(sigma))
    else:
        raise ValueError(f"sigma must be Decimal, int, or str, got {type(sigma)}")

    if sigma_dec < 0:
        raise ValueError(f"sigma must be non-negative, got {sigma_dec!r}")

    # Deterministic radius using Decimal only (no float)
    radius_dec = (Decimal("3") * sigma_dec).to_integral_value(rounding=ROUND_CEILING)
    radius_int = int(radius_dec)

    out = image.image.filter(ImageFilter.GaussianBlur(radius=radius_int))
    return ImageArtifact(out)
