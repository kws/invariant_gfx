"""gfx:threshold_alpha operation - applies a binary threshold to the alpha channel."""

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def threshold_alpha(image: ImageArtifact, t: int) -> ICacheable:
    """Apply binary threshold to alpha: alpha >= t -> 255, else 0. RGB unchanged.

    Args:
        image: ImageArtifact (source image).
        t: Threshold value, 0-255. Alpha >= t becomes 255, else 0.

    Returns:
        ImageArtifact with alpha thresholded.

    Raises:
        ValueError: If image is not an ImageArtifact or t is not in 0-255.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    if not isinstance(t, int) or t < 0 or t > 255:
        raise ValueError(f"t must be int in 0-255, got {t!r}")

    r, g, b, a = image.image.split()
    a_thresh = a.point(lambda x: 255 if x >= t else 0, mode="L")
    out = Image.merge("RGBA", (r, g, b, a_thresh))
    return ImageArtifact(out)
