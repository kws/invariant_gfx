"""gfx:tint operation - multiply-blends a color onto an image, preserving luminance structure."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def tint(
    image: ImageArtifact,
    color: tuple[int, int, int, int],
) -> ICacheable:
    """Multiply-blend a tint color onto the image's RGB. Preserves source alpha.

    Unlike colorize (which replaces RGB with a solid color), tint blends the
    color with the existing RGB, preserving the image's luminance and shading.

    Args:
        image: ImageArtifact (source image — full RGBA).
        color: Tuple[int, int, int, int] (RGB of tint, 0-255). Alpha component
            is ignored; source alpha is preserved.

    Returns:
        ImageArtifact with tinted RGB and original alpha.

    Raises:
        ValueError: If image is not an ImageArtifact or color is invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )
    r, g, b, _ = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    r_band, g_band, b_band, a_band = image.image.split()
    r_out = r_band.point(lambda x: (x * r) // 255, mode="L")
    g_out = g_band.point(lambda x: (x * g) // 255, mode="L")
    b_out = b_band.point(lambda x: (x * b) // 255, mode="L")
    out = Image.merge("RGBA", (r_out, g_out, b_out, a_band))
    return ImageArtifact(out)
