"""gfx:render_svg operation - converts SVG blobs into raster artifacts using cairosvg."""

from decimal import Decimal
from io import BytesIO
from typing import Any

import cairosvg
from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def render_svg(manifest: dict[str, Any]) -> ICacheable:
    """Convert SVG blobs into raster artifacts using cairosvg.

    Args:
        manifest: Must contain:
            - 'svg_content': str (inline SVG XML), bytes, or BlobArtifact
            - 'width': Decimal (target raster width in pixels)
            - 'height': Decimal (target raster height in pixels)

    Returns:
        ImageArtifact with rasterized SVG (RGBA mode).

    Raises:
        KeyError: If required keys are missing.
        ValueError: If SVG cannot be rendered or dimensions are invalid.
    """
    if "svg_content" not in manifest:
        raise KeyError("gfx:render_svg requires 'svg_content' in manifest")
    if "width" not in manifest:
        raise KeyError("gfx:render_svg requires 'width' in manifest")
    if "height" not in manifest:
        raise KeyError("gfx:render_svg requires 'height' in manifest")

    svg_content = manifest["svg_content"]
    width_val = manifest["width"]
    height_val = manifest["height"]

    # Convert to int (handles Decimal, int, or string)
    if isinstance(width_val, Decimal):
        width = int(width_val)
    elif isinstance(width_val, (int, str)):
        width = int(width_val)
    else:
        raise ValueError(f"width must be Decimal, int, or str, got {type(width_val)}")

    if isinstance(height_val, Decimal):
        height = int(height_val)
    elif isinstance(height_val, (int, str)):
        height = int(height_val)
    else:
        raise ValueError(f"height must be Decimal, int, or str, got {type(height_val)}")

    if width <= 0 or height <= 0:
        raise ValueError(f"size must be positive, got {width}x{height}")

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
            output_width=width,
            output_height=height,
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
