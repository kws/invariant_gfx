"""gfx:render_text operation - creates tight-fitting text artifacts using Pillow."""

from collections.abc import Callable
from decimal import Decimal
from functools import lru_cache
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont
from justmytype import get_default_registry

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact

_FIT_WIDTH_REFERENCE_SIZE = 64
_FIT_WIDTH_MIN_FILL_PERCENT = 95
_FIT_WIDTH_MAX_PROBES = 4
_FONT_BLOB_DATA: dict[str, bytes] = {}


@lru_cache(maxsize=256)
def _resolve_font_path_cached(
    font: str,
    weight: int | None,
    style: str,
) -> str:
    """Resolve a font family to a filesystem path."""
    registry = get_default_registry()
    font_info = registry.find_font(font, weight=weight, style=style)

    if font_info is None:
        raise ValueError(
            f"gfx:render_text failed to find font '{font}' "
            f"(weight={weight}, style={style})"
        )

    return str(font_info.path)


@lru_cache(maxsize=512)
def _load_font_path_cached(path: str, size_int: int) -> ImageFont.FreeTypeFont:
    """Load a font file path as a PIL ImageFont."""
    return ImageFont.truetype(path, size=size_int)


@lru_cache(maxsize=512)
def _load_font_blob_cached(blob_hash: str, size_int: int) -> ImageFont.FreeTypeFont:
    """Load font bytes as a PIL ImageFont."""
    return ImageFont.truetype(BytesIO(_FONT_BLOB_DATA[blob_hash]), size=size_int)


def _load_font(
    font: str | BlobArtifact,
    size_int: int,
    weight: int | None = None,
    style: str = "normal",
) -> ImageFont.FreeTypeFont:
    """Load a PIL ImageFont for the given font spec and size."""
    if isinstance(font, str):
        if weight is not None:
            if not isinstance(weight, int) or not (100 <= weight <= 900):
                raise ValueError(f"weight must be int in range 100-900, got {weight}")

        if style not in ("normal", "italic"):
            raise ValueError(f"style must be 'normal' or 'italic', got {style}")

        try:
            path = _resolve_font_path_cached(font, weight, style)
            return _load_font_path_cached(path, size_int)
        except Exception as e:
            raise ValueError(
                f"gfx:render_text failed to load font '{font}': {e}"
            ) from e

    elif isinstance(font, BlobArtifact):
        try:
            blob_hash = font.get_stable_hash()
            _FONT_BLOB_DATA.setdefault(blob_hash, font.data)
            return _load_font_blob_cached(blob_hash, size_int)
        except Exception as e:
            raise ValueError(
                f"gfx:render_text failed to load font from BlobArtifact: {e}"
            ) from e

    else:
        raise ValueError(f"font must be a string or BlobArtifact, got {type(font)}")


def _measure_loaded_text(
    text: str, pil_font: ImageFont.FreeTypeFont
) -> tuple[int, int]:
    """Measure text bounding box with a loaded font."""
    bbox = _text_bbox(text, pil_font)
    width = max(0, bbox[2] - bbox[0])
    height = max(0, bbox[3] - bbox[1])
    return (width, height)


def _text_bbox(
    text: str, pil_font: ImageFont.FreeTypeFont
) -> tuple[int, int, int, int]:
    """Return the text bounding box, preserving multiline ImageDraw behavior."""
    if "\n" in text:
        temp_image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_image)
        return temp_draw.textbbox((0, 0), text, font=pil_font)

    return pil_font.getbbox(text)


def _measure_text_width(
    text: str,
    font: str | BlobArtifact,
    size_int: int,
    weight: int | None = None,
    style: str = "normal",
) -> tuple[int, int]:
    """Measure text bounding box at given font size. Returns (width, height) in pixels."""
    pil_font = _load_font(font, size_int, weight, style)
    return _measure_loaded_text(text, pil_font)


def _render_at_size(
    text: str,
    pil_font: ImageFont.FreeTypeFont,
    color: tuple[int, int, int, int],
) -> ImageArtifact:
    """Render text with the given font to a tight-fitting ImageArtifact."""
    bbox = _text_bbox(text, pil_font)

    text_width = max(0, bbox[2] - bbox[0])
    text_height = max(0, bbox[3] - bbox[1])

    padding = 2
    image_width = text_width + padding * 2
    image_height = text_height + padding * 2

    image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    r, g, b, a = color
    text_x = padding - bbox[0]
    text_y = padding - bbox[1]
    draw.text((text_x, text_y), text, font=pil_font, fill=(r, g, b, a))

    return ImageArtifact(image)


def _fit_width_font_size(
    text: str,
    font: str | BlobArtifact,
    fit_width: Decimal,
    weight: int | None = None,
    style: str = "normal",
    exact: bool = False,
    measure_width: Callable[[int], int] | None = None,
) -> int:
    """Find a font size that fits and visually fills the requested width."""
    fit_width_int = int(fit_width)
    if fit_width_int <= 0:
        return 1

    if not text:
        return 1

    low = 1
    high = min(500, max(fit_width_int * 2, 100))

    measured_widths: dict[int, int] = {}

    def width_at(size_int: int) -> int:
        if size_int not in measured_widths:
            measured_widths[size_int] = (
                measure_width(size_int)
                if measure_width is not None
                else _measure_text_width(text, font, size_int, weight, style)[0]
            )
        return measured_widths[size_int]

    def fills_well(width: int) -> bool:
        return width * 100 >= fit_width_int * _FIT_WIDTH_MIN_FILL_PERCENT

    if exact:
        best = 1
        lower = low
        upper = high
        while lower <= upper:
            mid = (lower + upper) // 2
            if width_at(mid) <= fit_width_int:
                best = mid
                lower = mid + 1
            else:
                upper = mid - 1
        return best

    reference_size = min(_FIT_WIDTH_REFERENCE_SIZE, high)
    reference_width = width_at(reference_size)
    if reference_width <= 0:
        return high

    estimate = (fit_width_int * reference_size) // reference_width
    candidate = max(low, min(high, estimate))
    best_fit = 1
    first_too_wide = high + 1

    for _ in range(_FIT_WIDTH_MAX_PROBES):
        width = width_at(candidate)
        if width <= fit_width_int:
            best_fit = candidate
            if fills_well(width):
                return candidate
            if candidate >= high or candidate + 1 >= first_too_wide:
                return candidate

            next_candidate = (candidate * fit_width_int) // max(width, 1)
            next_candidate = max(candidate + 1, next_candidate)
            candidate = min(high, first_too_wide - 1, next_candidate)
            continue

        first_too_wide = candidate
        if candidate <= low:
            return best_fit

        next_candidate = (candidate * fit_width_int) // width
        next_candidate = min(candidate - 1, max(low, next_candidate))
        if next_candidate <= best_fit:
            if best_fit + 1 >= first_too_wide:
                return best_fit
            next_candidate = (best_fit + first_too_wide) // 2
            if next_candidate <= best_fit:
                return best_fit
        candidate = next_candidate

    return best_fit


def render_text(
    text: str,
    font: str | BlobArtifact,
    color: tuple[int, int, int, int],
    size: Decimal | int | str | None = None,
    fit_width: Decimal | int | None = None,
    weight: int | None = None,
    style: str = "normal",
    exact: bool = False,
) -> ICacheable:
    """Create a tight-fitting "Text Pill" artifact using Pillow.

    Either size or fit_width must be provided, but not both.

    Args:
        text: String content to render
        font: String (font family name) or BlobArtifact (font file bytes)
        color: Tuple[int, int, int, int] (RGBA, 0-255 per channel)
        size: Decimal | int | str (font size in points). Use when fixed size is desired.
        fit_width: Decimal | int (target max width in pixels). Use to estimate a
            font size that fits text within the width. Mutually exclusive with size.
        exact: bool (default False). When fit_width is provided, use True to find
            the largest fitting font size instead of the faster good-enough estimate.
        weight: int | None (font weight 100-900, optional, only for string fonts)
        style: str (font style: "normal" or "italic", default "normal", only for string fonts)

    Returns:
        ImageArtifact sized to the text bounding box (RGBA mode).

    Raises:
        ValueError: If font cannot be loaded, text cannot be rendered, or both/neither
            of size and fit_width are provided.
    """
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text)}")

    if not isinstance(exact, bool):
        raise ValueError(f"exact must be bool, got {type(exact)}")

    has_size = size is not None
    has_fit_width = fit_width is not None

    if has_size and has_fit_width:
        raise ValueError("must provide exactly one of size or fit_width, not both")
    if not has_size and not has_fit_width:
        raise ValueError("must provide either size or fit_width")

    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )

    r, g, b, a = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b, a)):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    if has_fit_width:
        fit_width_decimal = (
            Decimal(str(fit_width)) if not isinstance(fit_width, Decimal) else fit_width
        )
        size_int = _fit_width_font_size(
            text, font, fit_width_decimal, weight, style, exact
        )
    else:
        if isinstance(size, Decimal):
            size_int = int(size)
        elif isinstance(size, (int, str)):
            size_int = int(size)
        else:
            raise ValueError(f"size must be Decimal, int, or str, got {type(size)}")

        if size_int <= 0:
            raise ValueError(f"size must be positive, got {size_int}")

    pil_font = _load_font(font, size_int, weight, style)
    return _render_at_size(text, pil_font, color)
