"""gfx:thumbnail operation - resizes to fit a bounding box with aspect preservation."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def _to_int(value: Decimal | int | str) -> int:
    """Convert value to int."""
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, (int, str)):
        return int(value)
    raise ValueError(f"value must be Decimal, int, or str, got {type(value)}")


def thumbnail(
    image: ImageArtifact,
    width: Decimal | int | str,
    height: Decimal | int | str,
    mode: str = "contain",
) -> ICacheable:
    """Resize image to fit a bounding box with aspect preservation.

    Args:
        image: ImageArtifact (the image to thumbnail).
        width: Target bounding box width.
        height: Target bounding box height.
        mode: "contain" (letterbox — fit inside, pad to fill) or "cover"
            (crop — scale to fill, crop excess).

    Returns:
        ImageArtifact with exact dimensions (width, height).

    Raises:
        ValueError: If image is not an ImageArtifact, mode is invalid,
            or width/height are invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    if mode not in ("contain", "cover"):
        raise ValueError(f"mode must be 'contain' or 'cover', got {mode!r}")

    target_w = _to_int(width)
    target_h = _to_int(height)
    if target_w <= 0 or target_h <= 0:
        raise ValueError(
            f"width and height must be positive, got {target_w}x{target_h}"
        )

    orig_w = image.width
    orig_h = image.height
    if orig_w <= 0 or orig_h <= 0:
        raise ValueError(
            f"source image dimensions must be positive, got {orig_w}x{orig_h}"
        )

    ow = Decimal(orig_w)
    oh = Decimal(orig_h)
    tw = Decimal(target_w)
    th = Decimal(target_h)

    if mode == "contain":
        scale = min(tw / ow, th / oh)
    else:
        scale = max(tw / ow, th / oh)

    new_w = max(1, int((ow * scale).quantize(Decimal("1"))))
    new_h = max(1, int((oh * scale).quantize(Decimal("1"))))

    resized = image.image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    if mode == "contain":
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        canvas.paste(resized, (paste_x, paste_y))
        return ImageArtifact(canvas)
    else:
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        box = (left, top, left + target_w, top + target_h)
        cropped = resized.crop(box)
        return ImageArtifact(cropped)
