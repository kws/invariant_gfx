"""gfx:pad operation - expands the canvas with transparent padding."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def pad(
    image: ImageArtifact,
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> ICacheable:
    """Expand canvas by adding transparent padding around the image.

    Args:
        image: ImageArtifact (source image).
        left: Padding in pixels (left side).
        top: Padding in pixels (top).
        right: Padding in pixels (right side).
        bottom: Padding in pixels (bottom).

    Returns:
        ImageArtifact with original image placed at (left, top) in expanded canvas.

    Raises:
        ValueError: If image is not an ImageArtifact or any padding is not int or is negative.
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
    out_w = w + left + right
    out_h = h + top + bottom

    canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    canvas.paste(image.image, (left, top), image.image)
    return ImageArtifact(canvas)
