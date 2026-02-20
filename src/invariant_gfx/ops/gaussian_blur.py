"""gfx:gaussian_blur operation - applies Gaussian blur to an image."""

from decimal import Decimal

from PIL import ImageFilter

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def gaussian_blur(
    image: ImageArtifact,
    sigma: Decimal | int | str,
) -> ICacheable:
    """Apply Gaussian blur. Pillow's radius parameter is standard deviation (sigma).

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

    # Pillow's GaussianBlur(radius=...) is standard deviation; pass sigma directly.
    out = image.image.filter(ImageFilter.GaussianBlur(radius=float(sigma_dec)))
    return ImageArtifact(out)
