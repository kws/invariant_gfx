"""Recipe for packing multi-line text into a fixed box with greedy wrapping."""

from dataclasses import dataclass

from PIL import Image, ImageDraw
from invariant import Node, SubGraphNode, ref

from invariant_gfx.anchors import relative
from invariant_gfx.artifacts import BlobArtifact
from invariant_gfx.ops.render_text import _load_font


@dataclass(frozen=True)
class _PackedLayout:
    """Resolved text layout for packed_text()."""

    font_size: int
    lines: list[str]


def _measure_text(text: str, pil_font) -> tuple[int, int]:
    """Measure text using Pillow textbbox."""
    image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    bbox = draw.textbbox((0, 0), text, font=pil_font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _truncate_to_width(token: str, max_width: int, pil_font) -> str:
    """Fit a single token into max_width using a trailing ellipsis when required."""
    if max_width <= 0:
        return ""

    width, _ = _measure_text(token, pil_font)
    if width <= max_width:
        return token

    ellipsis = "…"
    ellipsis_width, _ = _measure_text(ellipsis, pil_font)
    if ellipsis_width > max_width:
        return ""

    low = 0
    high = len(token)
    best = ""
    while low <= high:
        mid = (low + high) // 2
        candidate = f"{token[:mid]}{ellipsis}"
        candidate_width, _ = _measure_text(candidate, pil_font)
        if candidate_width <= max_width:
            best = candidate
            low = mid + 1
        else:
            high = mid - 1

    return best or ellipsis


def _wrap_tokens(tokens: list[str], max_width: int, pil_font) -> list[str]:
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

        candidate_width, _ = _measure_text(candidate, pil_font)
        if candidate_width <= max_width:
            current_line.append(token)
            continue

        if current_line:
            lines.append(" ".join(current_line))
            current_line = [token]
            token_width, _ = _measure_text(token, pil_font)
            if token_width > max_width:
                current_line = [_truncate_to_width(token, max_width, pil_font)]
                lines.append(current_line[0])
                current_line = []
            continue

        lines.append(_truncate_to_width(token, max_width, pil_font))

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def _layout_height(lines: list[str], pil_font, line_gap: int) -> int:
    """Measure wrapped text height."""
    heights = [_measure_text(line, pil_font)[1] for line in lines]
    if not heights:
        return 0
    return sum(heights) + max(0, len(heights) - 1) * line_gap


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
) -> _PackedLayout:
    """Find largest font size whose wrapped lines fit height, then clamp if needed."""
    tokens = text.split()
    if not tokens:
        tokens = [""]

    best_layout: _PackedLayout | None = None
    for size in range(max_font_size, min_font_size - 1, -1):
        pil_font = _load_font(font, size, weight, style)
        lines = _wrap_tokens(tokens, width, pil_font)
        if _layout_height(lines, pil_font, line_gap) <= height:
            return _PackedLayout(font_size=size, lines=lines)
        best_layout = _PackedLayout(font_size=size, lines=lines)

    if best_layout is None:
        return _PackedLayout(font_size=min_font_size, lines=[""])

    # Still too tall at min size: drop from end until it fits, adding ellipsis on the last line.
    pil_font = _load_font(font, min_font_size, weight, style)
    lines = list(best_layout.lines)
    while lines and _layout_height(lines, pil_font, line_gap) > height:
        lines.pop()

    if not lines:
        return _PackedLayout(
            font_size=min_font_size,
            lines=[_truncate_to_width(text.strip(), width, pil_font)],
        )

    if len(lines) < len(best_layout.lines):
        lines[-1] = _truncate_to_width(f"{lines[-1]}…", width, pil_font)

    return _PackedLayout(font_size=min_font_size, lines=lines)


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


def packed_text(
    text: str,
    *,
    size: tuple[int, int],
    font: str | BlobArtifact,
    color: tuple[int, int, int, int] = (255, 255, 255, 255),
    min_font_size: int = 10,
    max_font_size: int | None = None,
    line_gap: int = 0,
    align_horizontal: str = "center",
    align_vertical: str = "center",
    weight: int | None = None,
    style: str = "normal",
) -> SubGraphNode:
    """Build a SubGraphNode that greedily packs multi-line text into a fixed size.

    The recipe pre-computes line wrapping and chosen font size when the graph is built,
    then emits a subgraph that renders each line, stacks lines using gfx:layout, and
    anchors that stack into a transparent fixed-size canvas with configurable alignment.
    """
    width, height = size
    if width <= 0 or height <= 0:
        raise ValueError(f"size values must be positive, got {size}")
    if min_font_size <= 0:
        raise ValueError(f"min_font_size must be positive, got {min_font_size}")
    if max_font_size is not None and max_font_size < min_font_size:
        raise ValueError(
            "max_font_size must be greater than or equal to min_font_size, "
            f"got min={min_font_size}, max={max_font_size}"
        )
    if line_gap < 0:
        raise ValueError(f"line_gap must be non-negative, got {line_gap}")

    resolved_max = max_font_size or max(min(width, height), min_font_size)
    layout = _fit_layout(
        text=text,
        font=font,
        width=width,
        height=height,
        min_font_size=min_font_size,
        max_font_size=resolved_max,
        line_gap=line_gap,
        weight=weight,
        style=style,
    )

    h_align = _to_axis_align(align_horizontal, "horizontal")
    v_align = _to_axis_align(align_vertical, "vertical")
    block_align = f"{h_align}{v_align}@{h_align}{v_align}"

    nodes: dict[str, Node] = {
        "canvas": Node(
            op_name="gfx:create_solid",
            params={"size": size, "color": (0, 0, 0, 0)},
            deps=[],
        ),
    }

    line_node_ids: list[str] = []
    for index, line in enumerate(layout.lines):
        node_id = f"line_{index}"
        nodes[node_id] = Node(
            op_name="gfx:render_text",
            params={
                "text": line,
                "font": font,
                "color": color,
                "size": layout.font_size,
                "weight": weight,
                "style": style,
            },
            deps=[],
        )
        line_node_ids.append(node_id)

    nodes["text_block"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": h_align,
            "gap": line_gap,
            "items": [ref(node_id) for node_id in line_node_ids],
        },
        deps=line_node_ids,
    )

    nodes["packed"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("canvas"), "id": "canvas"},
                {
                    "image": ref("text_block"),
                    "id": "text_block",
                    "anchor": relative("canvas", block_align),
                },
            ],
        },
        deps=["canvas", "text_block"],
    )

    return SubGraphNode(params={}, deps=[], graph=nodes, output="packed")
