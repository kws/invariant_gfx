"""gfx:crop_to_content operation - trims transparent pixels to content bounding box."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def crop_to_content(image: ImageArtifact) -> ICacheable:
    """Trim transparent pixels to the tight bounding box of non-transparent content.

    Uses getbbox() on the alpha channel to find pixels where alpha > 0.

    Args:
        image: ImageArtifact (source image).

    Returns:
        ImageArtifact cropped to content bounds, or 1x1 transparent pixel if fully transparent.

    Raises:
        ValueError: If image is not an ImageArtifact.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    _, _, _, a = image.image.split()
    bbox = a.getbbox()

    if bbox is None:
        return ImageArtifact(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))

    cropped = image.image.crop(bbox)
    return ImageArtifact(cropped)
