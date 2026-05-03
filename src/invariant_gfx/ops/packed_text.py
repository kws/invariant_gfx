"""gfx:packed_text operation - packs multi-line text into a fixed-size canvas."""

from dataclasses import dataclass
from decimal import Decimal

from PIL import Image, ImageFont

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import BlobArtifact, ImageArtifact
from invariant_gfx.ops.render_text import (
    _fit_width_font_size,
    _load_font,
    _measure_loaded_text,
    _render_at_size,
)

_TEXT_PADDING = 2  # Keep in sync with gfx:render_text padding.


@dataclass(frozen=True)
class _PackedLayout:
    """Resolved text layout for packed_text()."""

    font_size: int
    lines: list[str]


class _TextMeasurer:
    """Per-render cache for loaded fonts and text measurements."""

    def __init__(
        self,
        font: str | BlobArtifact,
        weight: int | None,
        style: str,
    ) -> None:
        self._font = font
        self._weight = weight
        self._style = style
        self._fonts: dict[int, ImageFont.FreeTypeFont] = {}
        self._measurements: dict[tuple[int, str], tuple[int, int]] = {}

    def font(self, size: int) -> ImageFont.FreeTypeFont:
        if size not in self._fonts:
            self._fonts[size] = _load_font(self._font, size, self._weight, self._style)
        return self._fonts[size]

    def measure(self, text: str, size: int) -> tuple[int, int]:
        key = (size, text)
        if key not in self._measurements:
            width, height = _measure_loaded_text(text, self.font(size))
            self._measurements[key] = (
                width + _TEXT_PADDING * 2,
                height + _TEXT_PADDING * 2,
            )
        return self._measurements[key]


def _truncate_to_width(
    token: str,
    max_width: int,
    measurer: _TextMeasurer,
    font_size: int,
) -> str:
    """Fit a single token into max_width using a trailing ellipsis when required."""
    if max_width <= 0:
        return ""

    width, _ = measurer.measure(token, font_size)
    if width <= max_width:
        return token

    ellipsis = "\u2026"
    ellipsis_width, _ = measurer.measure(ellipsis, font_size)
    if ellipsis_width > max_width:
        return ""

    low = 0
    high = len(token)
    best = ""
    while low <= high:
        mid = (low + high) // 2
        candidate = f"{token[:mid]}{ellipsis}"
        candidate_width, _ = measurer.measure(candidate, font_size)
        if candidate_width <= max_width:
            best = candidate
            low = mid + 1
        else:
            high = mid - 1

    return best or ellipsis


def _wrap_tokens(
    tokens: list[str],
    max_width: int,
    measurer: _TextMeasurer,
    font_size: int,
) -> list[str]:
    """Greedy token wrapping with horizontal truncation for oversized tokens."""
    if not tokens:
        return [""]

    lines: list[str] = []
    current_line: list[str] = []

    for token in tokens:
        if not current_line:
            candidate = token
        else:
            candidate = f"{' '.join(current_line)} {token}"

        candidate_width, _ = measurer.measure(candidate, font_size)
        if candidate_width <= max_width:
            current_line.append(token)
            continue

        if current_line:
            lines.append(" ".join(current_line))
            current_line = [token]
            token_width, _ = measurer.measure(token, font_size)
            if token_width > max_width:
                current_line = [
                    _truncate_to_width(token, max_width, measurer, font_size)
                ]
                lines.append(current_line[0])
                current_line = []
            continue

        lines.append(_truncate_to_width(token, max_width, measurer, font_size))

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def _layout_height(
    lines: list[str],
    measurer: _TextMeasurer,
    font_size: int,
    line_gap: int,
) -> int:
    """Measure wrapped text height."""
    heights = [measurer.measure(line, font_size)[1] for line in lines]
    if not heights:
        return 0
    return sum(heights) + max(0, len(heights) - 1) * line_gap


def _max_font_size_without_truncation(
    tokens: list[str],
    font: str | BlobArtifact,
    width: int,
    max_font_size: int,
    weight: int | None,
    style: str,
    measurer: _TextMeasurer,
) -> int | None:
    """Estimate a large font size where every token fits within width."""
    non_empty_tokens = [token for token in tokens if token]
    if not non_empty_tokens:
        return max_font_size

    fit_width_value = width - _TEXT_PADDING * 2
    if fit_width_value <= 0:
        return None

    fit_width = Decimal(str(fit_width_value))
    best = max_font_size
    token_limits: dict[str, int] = {}
    for token in non_empty_tokens:
        token_width, _ = measurer.measure(token, 1)
        if token_width > width:
            return None
        token_width_at_best, _ = measurer.measure(token, best)
        if token_width_at_best <= width:
            continue
        if token not in token_limits:
            token_limits[token] = _fit_width_font_size(
                token,
                font,
                fit_width,
                weight,
                style,
                measure_width=lambda size, token=token: max(
                    0, measurer.measure(token, size)[0] - _TEXT_PADDING * 2
                ),
            )
        token_max = token_limits[token]
        best = min(best, token_max)
        if best <= 0:
            return None
    return best


def _drop_lines_to_fit(
    *,
    text: str,
    tokens: list[str],
    font: str | BlobArtifact,
    width: int,
    height: int,
    font_size: int,
    line_gap: int,
    weight: int | None,
    style: str,
    measurer: _TextMeasurer,
) -> _PackedLayout:
    """Drop trailing lines until the layout fits height, adding ellipsis if needed."""
    lines = _wrap_tokens(tokens, width, measurer, font_size)
    original_count = len(lines)

    while lines and _layout_height(lines, measurer, font_size, line_gap) > height:
        lines.pop()

    if not lines:
        return _PackedLayout(
            font_size=font_size,
            lines=[_truncate_to_width(text.strip(), width, measurer, font_size)],
        )

    if len(lines) < original_count:
        tail = lines[-1]
        if not tail.endswith("\u2026"):
            tail = f"{tail}\u2026"
        lines[-1] = _truncate_to_width(tail, width, measurer, font_size)

    return _PackedLayout(font_size=font_size, lines=lines)


def _find_layout_by_height(
    tokens: list[str],
    font: str | BlobArtifact,
    width: int,
    height: int,
    min_font_size: int,
    max_font_size: int,
    line_gap: int,
    weight: int | None,
    style: str,
    measurer: _TextMeasurer,
) -> _PackedLayout | None:
    """Binary-search the largest font size whose wrapped lines fit height."""
    low = min_font_size
    high = max_font_size
    best_layout: _PackedLayout | None = None

    while low <= high:
        mid = (low + high) // 2
        lines = _wrap_tokens(tokens, width, measurer, mid)
        if _layout_height(lines, measurer, mid, line_gap) <= height:
            best_layout = _PackedLayout(font_size=mid, lines=lines)
            low = mid + 1
        else:
            high = mid - 1

    return best_layout


def _fit_layout(
    text: str,
    font: str | BlobArtifact,
    width: int,
    height: int,
    min_font_size: int,
    max_font_size: int,
    line_gap: int,
    weight: int | None,
    style: str,
    measurer: _TextMeasurer,
) -> _PackedLayout:
    """Find a large font size whose wrapped lines fit height, then clamp if needed."""
    tokens = text.split()
    if not tokens:
        tokens = [""]

    max_no_trunc = _max_font_size_without_truncation(
        tokens=tokens,
        font=font,
        width=width,
        max_font_size=max_font_size,
        weight=weight,
        style=style,
        measurer=measurer,
    )
    if max_no_trunc is not None and max_no_trunc >= min_font_size:
        layout = _find_layout_by_height(
            tokens=tokens,
            font=font,
            width=width,
            height=height,
            min_font_size=min_font_size,
            max_font_size=max_no_trunc,
            line_gap=line_gap,
            weight=weight,
            style=style,
            measurer=measurer,
        )
        if layout is not None:
            return layout
        return _drop_lines_to_fit(
            text=text,
            tokens=tokens,
            font=font,
            width=width,
            height=height,
            font_size=min_font_size,
            line_gap=line_gap,
            weight=weight,
            style=style,
            measurer=measurer,
        )

    layout = _find_layout_by_height(
        tokens=tokens,
        font=font,
        width=width,
        height=height,
        min_font_size=min_font_size,
        max_font_size=max_font_size,
        line_gap=line_gap,
        weight=weight,
        style=style,
        measurer=measurer,
    )
    if layout is not None:
        return layout

    return _drop_lines_to_fit(
        text=text,
        tokens=tokens,
        font=font,
        width=width,
        height=height,
        font_size=min_font_size,
        line_gap=line_gap,
        weight=weight,
        style=style,
        measurer=measurer,
    )


def _to_axis_align(value: str, axis: str) -> str:
    """Normalize user-friendly alignment names to composite alignment chars."""
    aliases = {
        "s": "s",
        "start": "s",
        "left": "s",
        "top": "s",
        "c": "c",
        "center": "c",
        "middle": "c",
        "e": "e",
        "end": "e",
        "right": "e",
        "bottom": "e",
    }
    if value not in aliases:
        raise ValueError(f"invalid {axis} alignment '{value}'")
    return aliases[value]


def _to_int(value, *, name: str) -> int:
    """Convert value to int, handling Decimal, int, or str."""
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(Decimal(value))
        except Exception as exc:
            raise ValueError(
                f"{name} must be an int-compatible string, got '{value}'"
            ) from exc
    raise ValueError(f"{name} must be int, Decimal, or str, got {type(value)}")


def packed_text(
    text: str,
    size: tuple[int, int] | list[int],
    font: str | BlobArtifact,
    color: tuple[int, int, int, int] = (255, 255, 255, 255),
    min_font_size: int = 10,
    max_font_size: int | None = None,
    line_gap: Decimal | int | str = 0,
    align_horizontal: str = "center",
    align_vertical: str = "center",
    weight: int | None = None,
    style: str = "normal",
) -> ICacheable:
    """Render packed multi-line text into a fixed-size RGBA canvas.

    Args:
        text: String content to render.
        size: Tuple/list (width, height) in pixels.
        font: String (font family name) or BlobArtifact (font file bytes).
        color: Tuple[int, int, int, int] (RGBA, 0-255 per channel).
        min_font_size: Smallest font size allowed.
        max_font_size: Optional maximum font size.
        line_gap: Gap between lines in pixels.
        align_horizontal: "start"/"center"/"end" (or aliases).
        align_vertical: "top"/"center"/"bottom" (or aliases).
        weight: Font weight (100-900, optional, only for string fonts).
        style: Font style: "normal" or "italic".

    Returns:
        ImageArtifact sized to the requested canvas (RGBA mode).
    """
    if not isinstance(text, str):
        raise ValueError(f"text must be a string, got {type(text)}")

    if not isinstance(size, (tuple, list)) or len(size) != 2:
        raise ValueError(f"size must be a tuple/list of (width, height), got {size}")

    width = _to_int(size[0], name="size[0]")
    height = _to_int(size[1], name="size[1]")
    if width <= 0 or height <= 0:
        raise ValueError(f"size values must be positive, got {size}")

    min_font_size_int = _to_int(min_font_size, name="min_font_size")
    if min_font_size_int <= 0:
        raise ValueError(f"min_font_size must be positive, got {min_font_size}")

    max_font_size_int: int | None = None
    if max_font_size is not None:
        max_font_size_int = _to_int(max_font_size, name="max_font_size")
        if max_font_size_int < min_font_size_int:
            raise ValueError(
                "max_font_size must be greater than or equal to min_font_size, "
                f"got min={min_font_size_int}, max={max_font_size_int}"
            )

    line_gap_int = _to_int(line_gap, name="line_gap")
    if line_gap_int < 0:
        raise ValueError(f"line_gap must be non-negative, got {line_gap}")

    if not isinstance(color, (tuple, list)) or len(color) != 4:
        raise ValueError(
            f"color must be a tuple/list of 4 RGBA values, got {type(color)}"
        )

    r, g, b, a = color
    if not all(isinstance(c, int) and 0 <= c <= 255 for c in (r, g, b, a)):
        raise ValueError(f"color values must be int in range 0-255, got {color}")

    resolved_max = max_font_size_int or max(min(width, height), min_font_size_int)
    measurer = _TextMeasurer(font, weight, style)
    layout = _fit_layout(
        text=text,
        font=font,
        width=width,
        height=height,
        min_font_size=min_font_size_int,
        max_font_size=resolved_max,
        line_gap=line_gap_int,
        weight=weight,
        style=style,
        measurer=measurer,
    )

    h_align = _to_axis_align(align_horizontal, "horizontal")
    v_align = _to_axis_align(align_vertical, "vertical")

    pil_font = measurer.font(layout.font_size)
    line_images = [_render_at_size(line, pil_font, color) for line in layout.lines]

    block_width = max(image.width for image in line_images)
    block_height = sum(image.height for image in line_images) + line_gap_int * (
        len(line_images) - 1
    )

    block = Image.new("RGBA", (block_width, block_height), (0, 0, 0, 0))
    y = 0
    for image in line_images:
        if h_align == "s":
            x = 0
        elif h_align == "c":
            x = (block_width - image.width) // 2
        else:
            x = block_width - image.width

        block.alpha_composite(image.image, (x, y))
        y += image.height + line_gap_int

    if h_align == "s":
        block_x = 0
    elif h_align == "c":
        block_x = (width - block_width) // 2
    else:
        block_x = width - block_width

    if v_align == "s":
        block_y = 0
    elif v_align == "c":
        block_y = (height - block_height) // 2
    else:
        block_y = height - block_height

    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    canvas.alpha_composite(block, (block_x, block_y))

    return ImageArtifact(canvas)
