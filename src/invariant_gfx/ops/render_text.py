"""gfx:render_text operation - creates tight-fitting text artifacts using Pillow."""

from decimal import Decimal
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from justmytype import get_default_registry

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact


def render_text(
    text: str,
    font: str | BlobArtifact,
    size: Decimal | int | str,
    color: tuple[int, int, int, int],
    weight: int | None = None,
    style: str = "normal",
) -> ICacheable:
    """Create a tight-fitting "Text Pill" artifact using Pillow.

    Args:
        text: String content to render
        font: String (font family name) or BlobArtifact (font file bytes)
        size: Decimal | int | str (font size in points)
        color: Tuple[int, int, int, int] (RGBA, 0-255 per channel)
        weight: int | None (font weight 100-900, optional, only for string fonts)
        style: str (font style: "normal" or "italic", default "normal", only for string fonts)

    Returns:
        ImageArtifact sized to the text bounding box (RGBA mode).

    Raises:
        ValueError: If font cannot be loaded or text cannot be rendered.
    """
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text)}")

    # Convert size to int
    if isinstance(size, Decimal):
        size_int = int(size)
    elif isinstance(size, (int, str)):
        size_int = int(size)
    else:
        raise ValueError(f"size must be Decimal, int, or str, got {type(size)}")

    if size_int <= 0:
        raise ValueError(f"size must be positive, got {size_int}")

    # Validate color
    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )

    r, g, b, a = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b, a)):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    # Load font
    if isinstance(font, str):
        # String font name - resolve via JustMyType
        if weight is not None:
            if not isinstance(weight, int) or not (100 <= weight <= 900):
                raise ValueError(f"weight must be int in range 100-900, got {weight}")

        if style not in ("normal", "italic"):
            raise ValueError(f"style must be 'normal' or 'italic', got {style}")

        registry = get_default_registry()
        font_info = registry.find_font(font, weight=weight, style=style)

        if font_info is None:
            raise ValueError(
                f"gfx:render_text failed to find font '{font}' "
                f"(weight={weight}, style={style})"
            )

        try:
            pil_font = font_info.load(size=size_int)
        except Exception as e:
            raise ValueError(
                f"gfx:render_text failed to load font '{font}': {e}"
            ) from e

    elif isinstance(font, BlobArtifact):
        # BlobArtifact font - load directly
        # weight and style are ignored for BlobArtifact fonts
        try:
            pil_font = ImageFont.truetype(BytesIO(font.data), size=size_int)
        except Exception as e:
            raise ValueError(
                f"gfx:render_text failed to load font from BlobArtifact: {e}"
            ) from e

    else:
        raise ValueError(f"font must be a string or BlobArtifact, got {type(font)}")

    # Get text bounding box
    # Use a temporary image to measure text
    temp_image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_image)
    bbox = temp_draw.textbbox((0, 0), text, font=pil_font)

    # Calculate tight bounding box
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Create image with tight bounding box
    # Add small padding to avoid clipping
    padding = 2
    image_width = text_width + padding * 2
    image_height = text_height + padding * 2

    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw text (offset by padding and bbox offset)
    text_x = padding - bbox[0]
    text_y = padding - bbox[1]
    draw.text((text_x, text_y), text, font=pil_font, fill=(r, g, b, a))

    return ImageArtifact(image)
