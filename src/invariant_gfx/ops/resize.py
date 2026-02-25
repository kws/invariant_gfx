"""gfx:resize operation - scales an ImageArtifact to target dimensions."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def _to_int(value: Decimal | int | str | None) -> int | None:
    """Convert value to int, or return None if value is None."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, (int, str)):
        return int(value)
    raise ValueError(f"value must be Decimal, int, str, or None, got {type(value)}")


def _to_decimal(value: Decimal | int | str | None) -> Decimal | None:
    """Convert value to Decimal, or return None if value is None."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, str)):
        return Decimal(str(value))
    raise ValueError(f"value must be Decimal, int, str, or None, got {type(value)}")


def resize(
    image: ImageArtifact,
    width: Decimal | int | str | None = None,
    height: Decimal | int | str | None = None,
    scale: Decimal | int | str | None = None,
) -> ICacheable:
    """Scale an ImageArtifact to target dimensions.

    Provide either (width and/or height) or scale. Scale is mutually exclusive
    with width and height. If only one of width or height is provided, the
    other is computed proportionally to preserve aspect ratio.

    Args:
        image: ImageArtifact (the image to resize)
        width: Decimal | int | str | None (target width; optional if height or scale provided)
        height: Decimal | int | str | None (target height; optional if width or scale provided)
        scale: Decimal | int | str | None (uniform scale factor; mutually exclusive with width/height)

    Returns:
        ImageArtifact with resized image (RGBA mode).

    Raises:
        ValueError: If image is not an ImageArtifact, invalid param combination,
            source dimensions are zero, or width/height/scale values are invalid.
    """
    if not isinstance(image, ImageArtifact):
        raise ValueError(f"image must be ImageArtifact, got {type(image)}")

    scale_dec = _to_decimal(scale)
    width_int = _to_int(width)
    height_int = _to_int(height)

    if scale_dec is not None:
        if width_int is not None or height_int is not None:
            raise ValueError("scale is mutually exclusive with width and height")
        if scale_dec <= 0:
            raise ValueError(f"scale must be positive, got {scale_dec}")
    elif width_int is None and height_int is None:
        raise ValueError("at least one of width, height, or scale must be provided")

    orig_w = image.width
    orig_h = image.height
    if orig_w <= 0 or orig_h <= 0:
        raise ValueError(
            f"source image dimensions must be positive, got {orig_w}x{orig_h}"
        )

    if scale_dec is not None:
        width_int = max(
            1,
            int((Decimal(orig_w) * scale_dec).quantize(Decimal("1"))),
        )
        height_int = max(
            1,
            int((Decimal(orig_h) * scale_dec).quantize(Decimal("1"))),
        )
    elif width_int is not None and height_int is not None:
        # Both provided: use explicit dimensions
        pass
    elif width_int is not None:
        # Only width: compute height proportionally
        height_int = max(
            1,
            int(
                (Decimal(orig_h) * Decimal(width_int) / Decimal(orig_w)).quantize(
                    Decimal("1")
                )
            ),
        )
    else:
        # Only height: compute width proportionally
        width_int = max(
            1,
            int(
                (Decimal(orig_w) * Decimal(height_int) / Decimal(orig_h)).quantize(
                    Decimal("1")
                )
            ),
        )

    if width_int <= 0 or height_int <= 0:
        raise ValueError(f"size must be positive, got {width_int}x{height_int}")

    resized_image = image.image.resize(
        (width_int, height_int), Image.Resampling.LANCZOS
    )

    return ImageArtifact(resized_image)
