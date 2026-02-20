"""gfx:translate operation - offsets an image by (dx, dy), expanding the canvas."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def translate(image: ImageArtifact, dx: int, dy: int) -> ICacheable:
    """Offset image by (dx, dy), expanding the canvas. Vacated area is transparent.

    Args:
        image: ImageArtifact (source image).
        dx: Horizontal offset in pixels (positive = right).
        dy: Vertical offset in pixels (positive = down).

    Returns:
        ImageArtifact with translated content on expanded canvas.

    Raises:
        ValueError: If image is not an ImageArtifact or dx/dy are not int.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    if not isinstance(dx, int):
        raise ValueError(f"dx must be int, got {type(dx)}")
    if not isinstance(dy, int):
        raise ValueError(f"dy must be int, got {type(dy)}")

    w, h = image.image.size
    out_w = w + abs(dx)
    out_h = h + abs(dy)
    paste_x = dx if dx >= 0 else 0
    paste_y = dy if dy >= 0 else 0

    canvas = Image.new("RGBA", (out_w, out_h), (0, 0, 0, 0))
    canvas.paste(image.image, (paste_x, paste_y), image.image)
    return ImageArtifact(canvas)
