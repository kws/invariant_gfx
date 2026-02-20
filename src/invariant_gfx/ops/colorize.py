"""gfx:colorize operation - fills an image with a solid color, preserving alpha shape."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def colorize(
    image: ImageArtifact,
    color: tuple[int, int, int, int],
) -> ICacheable:
    """Fill image with solid color; output alpha = source alpha × color alpha (per pixel).

    Args:
        image: ImageArtifact (source — typically an alpha-only mask).
        color: Tuple[int, int, int, int] (RGBA, 0-255 per channel).

    Returns:
        ImageArtifact with RGB set to color and alpha = (source_alpha * color_alpha) / 255.

    Raises:
        ValueError: If image is not an ImageArtifact or color is invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )
    r, g, b, a_c = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b, a_c)):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    _, _, _, a_src = image.image.split()
    w, h = image.image.size
    r_band = Image.new("L", (w, h), r)
    g_band = Image.new("L", (w, h), g)
    b_band = Image.new("L", (w, h), b)
    a_out = a_src.point(lambda x: int(x * a_c / 255), mode="L")
    out = Image.merge("RGBA", (r_band, g_band, b_band, a_out))
    return ImageArtifact(out)
