"""gfx:mask_alpha operation - applies a mask to an image's alpha channel."""

from PIL import Image, ImageChops

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def mask_alpha(image: ImageArtifact, mask: ImageArtifact) -> ICacheable:
    """Apply mask to alpha: output alpha = image_alpha * mask_alpha (per pixel). RGB unchanged.

    Args:
        image: ImageArtifact (source image).
        mask: ImageArtifact (mask image; alpha channel used).

    Returns:
        ImageArtifact with source RGB and alpha = image_alpha * mask_alpha / 255.

    Raises:
        ValueError: If image or mask is not an ImageArtifact, or if dimensions differ.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")
    if not isinstance(mask, ImageArtifact):
        raise ValueError(f"mask must be ImageArtifact, got {type(mask)}")
    if image.image.size != mask.image.size:
        raise ValueError(
            f"image and mask must have same dimensions, "
            f"got {image.image.size} and {mask.image.size}"
        )

    r, g, b, a_img = image.image.split()
    _, _, _, a_mask = mask.image.split()
    a_out = ImageChops.multiply(a_img, a_mask)
    out = Image.merge("RGBA", (r, g, b, a_out))
    return ImageArtifact(out)
