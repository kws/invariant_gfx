"""gfx:extract_alpha operation - extracts the alpha channel from an image."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def extract_alpha(image: ImageArtifact) -> ICacheable:
    """Extract the alpha channel from an image; RGB channels are zeroed.

    Args:
        image: ImageArtifact (source image).

    Returns:
        ImageArtifact with RGB zeroed and alpha preserved from source.

    Raises:
        ValueError: If image is not an ImageArtifact.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    r, g, b, a = image.image.split()
    zero = Image.new("L", image.image.size, 0)
    out = Image.merge("RGBA", (zero, zero, zero, a))
    return ImageArtifact(out)
