"""gfx:crop operation - shrinks the canvas by removing pixels from the edges."""

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def crop(
    image: ImageArtifact,
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> ICacheable:
    """Shrink canvas by removing pixels from the edges (inverse of pad).

    Args:
        image: ImageArtifact (source image).
        left: Pixels to remove from left edge.
        top: Pixels to remove from top edge.
        right: Pixels to remove from right edge.
        bottom: Pixels to remove from bottom edge.

    Returns:
        ImageArtifact with rectangle from (left, top) to (width - right, height - bottom).

    Raises:
        ValueError: If image is not an ImageArtifact, any inset is not int or is negative,
            or left+right >= width or top+bottom >= height (output would have non-positive dimensions).
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    for name, val in (
        ("left", left),
        ("top", top),
        ("right", right),
        ("bottom", bottom),
    ):
        if not isinstance(val, int):
            raise ValueError(f"{name} must be int, got {type(val)}")
        if val < 0:
            raise ValueError(f"{name} must be non-negative, got {val}")

    w, h = image.image.size
    if left + right >= w:
        raise ValueError(
            f"left + right must be less than width ({w}), got left={left} right={right}"
        )
    if top + bottom >= h:
        raise ValueError(
            f"top + bottom must be less than height ({h}), got top={top} bottom={bottom}"
        )

    box = (left, top, w - right, h - bottom)
    cropped = image.image.crop(box)
    return ImageArtifact(cropped)
