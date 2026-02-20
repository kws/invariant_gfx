"""gfx:dilate operation - expands the alpha channel by a given radius."""

from PIL import Image, ImageFilter

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def dilate(image: ImageArtifact, radius: int) -> ICacheable:
    """Expand (grow) the alpha channel by radius pixels. RGB unchanged.

    Uses Pillow MaxFilter with kernel size 2*radius+1 on the alpha band only.

    Args:
        image: ImageArtifact (source image).
        radius: Expansion radius in pixels (non-negative).

    Returns:
        ImageArtifact with alpha channel dilated.

    Raises:
        ValueError: If image is not an ImageArtifact or radius is negative.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    if not isinstance(radius, int) or radius < 0:
        raise ValueError(f"radius must be non-negative int, got {radius!r}")

    r, g, b, a = image.image.split()
    size = 2 * radius + 1
    a_dilated = a.filter(ImageFilter.MaxFilter(size=size))
    out = Image.merge("RGBA", (r, g, b, a_dilated))
    return ImageArtifact(out)
