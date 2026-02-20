"""gfx:invert_alpha operation - inverts the alpha channel of an image."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def invert_alpha(image: ImageArtifact) -> ICacheable:
    """Invert the alpha channel of an image (255 - alpha). RGB unchanged.

    Args:
        image: ImageArtifact (source image, typically alpha-channel from extract_alpha).

    Returns:
        ImageArtifact with alpha values inverted.

    Raises:
        ValueError: If image is not an ImageArtifact.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    r, g, b, a = image.image.split()
    a_inv = a.point(lambda x: 255 - x, mode="L")
    out = Image.merge("RGBA", (r, g, b, a_inv))
    return ImageArtifact(out)
