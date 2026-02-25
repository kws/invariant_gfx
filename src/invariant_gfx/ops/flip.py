"""gfx:flip operation - flips an ImageArtifact horizontally and/or vertically."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def flip(
    image: ImageArtifact,
    horizontal: bool = False,
    vertical: bool = False,
) -> ICacheable:
    """Flip an ImageArtifact horizontally and/or vertically.

    Args:
        image: ImageArtifact (the image to flip).
        horizontal: Flip left-right.
        vertical: Flip top-bottom.
        If both False: no-op — return the same ImageArtifact instance.

    Returns:
        ImageArtifact with flipped image (or unchanged if both False).

    Raises:
        ValueError: If image is not an ImageArtifact.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    if not horizontal and not vertical:
        return image

    result = image.image
    if horizontal:
        result = result.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if vertical:
        result = result.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

    return ImageArtifact(result)
