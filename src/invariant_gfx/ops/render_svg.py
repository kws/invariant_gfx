"""gfx:render_svg operation - converts SVG blobs into raster artifacts using cairosvg."""

from decimal import Decimal
from io import BytesIO

import cairosvg
from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def render_svg(
    svg_content: str | bytes | BlobArtifact,
    width: Decimal | int | str,
    height: Decimal | int | str,
) -> ICacheable:
    """Convert SVG blobs into raster artifacts using cairosvg.

    Args:
        svg_content: str (inline SVG XML), bytes, or BlobArtifact
        width: Decimal | int | str (target raster width in pixels)
        height: Decimal | int | str (target raster height in pixels)

    Returns:
        ImageArtifact with rasterized SVG (RGBA mode).

    Raises:
        ValueError: If SVG cannot be rendered or dimensions are invalid.
    """
    # Convert to int (handles Decimal, int, or string)
    if isinstance(width, Decimal):
        width_int = int(width)
    elif isinstance(width, (int, str)):
        width_int = int(width)
    else:
        raise ValueError(f"width must be Decimal, int, or str, got {type(width)}")

    if isinstance(height, Decimal):
        height_int = int(height)
    elif isinstance(height, (int, str)):
        height_int = int(height)
    else:
        raise ValueError(f"height must be Decimal, int, or str, got {type(height)}")

    if width_int <= 0 or height_int <= 0:
        raise ValueError(f"size must be positive, got {width_int}x{height_int}")

    # Extract SVG bytes from svg_content
    if isinstance(svg_content, str):
        # Inline SVG string - encode to bytes
        svg_bytes = svg_content.encode("utf-8")
    elif isinstance(svg_content, bytes):
        # Raw bytes (e.g., from ${blob.data} expression)
        svg_bytes = svg_content
    elif isinstance(svg_content, BlobArtifact):
        # BlobArtifact - extract data
        svg_bytes = svg_content.data
    else:
        raise ValueError(
            f"svg_content must be str, bytes, or BlobArtifact, got {type(svg_content)}"
        )

    # Render SVG to PNG using cairosvg
    try:
        png_bytes = cairosvg.svg2png(
            bytestring=svg_bytes,
            output_width=width_int,
            output_height=height_int,
        )
    except Exception as e:
        raise ValueError(f"gfx:render_svg failed to render SVG: {e}") from e

    # Parse PNG into PIL Image
    try:
        image = Image.open(BytesIO(png_bytes))
        # Convert to RGBA mode
        if image.mode != "RGBA":
            image = image.convert("RGBA")
    except Exception as e:
        raise ValueError(f"gfx:render_svg failed to parse rendered PNG: {e}") from e

    return ImageArtifact(image)
