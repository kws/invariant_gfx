"""gfx:grayscale operation - converts an image to grayscale, preserving alpha."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def grayscale(image: ImageArtifact) -> ICacheable:
    """Convert RGB to grayscale using the standard luminance formula, preserve alpha.

    Uses PIL's convert("L") which applies ITU-R BT.601: 0.299*R + 0.587*G + 0.114*B.

    Args:
        image: ImageArtifact (source image).

    Returns:
        ImageArtifact with grayscale RGB and original alpha preserved.

    Raises:
        ValueError: If image is not an ImageArtifact.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    r, g, b, a = image.image.split()
    gray = image.image.convert("L")
    out = Image.merge("RGBA", (gray, gray, gray, a))
    return ImageArtifact(out)
