"""gfx:composite operation - fixed-size composition engine."""

from decimal import Decimal
from typing import Any

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact

_SUPPORTED_BLEND_MODES = frozenset(
    {"normal", "multiply", "screen", "overlay", "darken", "lighten", "add"}
)


def composite(layers: list[dict[str, Any]]) -> ICacheable:
    """Composite multiple layers onto a fixed-size canvas.

    Args:
        layers: List of layer dicts, ordered by z-order (first drawn first, i.e. bottommost).
            Each layer dict must contain:
            - 'image': ImageArtifact (the layer content, resolved from ref() during Phase 1)
            - 'anchor': dict (required for all layers except the first, forbidden on first)
            - 'id': str (optional, required if referenced by relative() anchor)
            - 'mode': str (optional, default "normal")
            - 'opacity': Decimal (optional, default 1.0)

    Returns:
        ImageArtifact with composited result.

    Raises:
        ValueError: If layers structure is invalid, first layer has anchor, or positioning fails.
    """
    # Validate layers is a list
    if not isinstance(layers, list):
        raise ValueError(f"layers must be a list, got {type(layers)}")

    if len(layers) == 0:
        raise ValueError("layers must contain at least one layer")

    # Validate first layer (no anchor, must have image)
    first_layer = layers[0]
    if "anchor" in first_layer:
        raise ValueError("First layer must not have an 'anchor' field")
    if "image" not in first_layer:
        raise ValueError("First layer must have 'image' field")

    # Get canvas size from first layer
    first_image = first_layer["image"]
    if not isinstance(first_image, ImageArtifact):
        raise ValueError("First layer image must be ImageArtifact")
    canvas_width = first_image.width
    canvas_height = first_image.height

    # Validate subsequent layers (must have anchor and image)
    for i, layer in enumerate(layers[1:], start=1):
        if "anchor" not in layer:
            raise ValueError(f"Layer {i} must have 'anchor' field")
        if "image" not in layer:
            raise ValueError(f"Layer {i} must have 'image' field")

    # Create canvas
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    # Track placed layers for relative positioning (by id field)
    placed: dict[str, tuple[int, int, int, int]] = {}  # id -> (x, y, width, height)

    # Process layers in list order (z-order = list position)
    for layer in layers:
        image = layer["image"]
        if not isinstance(image, ImageArtifact):
            raise ValueError(f"Layer image must be ImageArtifact, got {type(image)}")

        layer_id = layer.get("id")  # Optional, but needed for relative() references
        anchor = layer.get("anchor")  # None for first layer
        mode = layer.get("mode", "normal")
        opacity_val = layer.get("opacity", 1.0)

        # Resolve position
        if anchor is None:
            # First layer at origin
            x, y = 0, 0
        else:
            x, y = _resolve_position(
                anchor, image, layer_id, placed, canvas_width, canvas_height
            )

        # Convert opacity
        if isinstance(opacity_val, Decimal):
            opacity = float(opacity_val)
        elif isinstance(opacity_val, (int, float, str)):
            opacity = float(opacity_val)
        else:
            opacity = 1.0

        opacity = max(0.0, min(1.0, opacity))  # Clamp to [0, 1]

        # Apply opacity if needed
        layer_image = image.image
        if opacity < 1.0:
            # Create a copy with adjusted alpha
            layer_image = layer_image.copy()
            alpha = layer_image.split()[3]
            alpha = alpha.point(lambda p: int(p * opacity))
            layer_image.putalpha(alpha)

        # Validate blend mode
        if mode not in _SUPPORTED_BLEND_MODES:
            raise ValueError(
                f"Unknown blend mode '{mode}', must be one of {sorted(_SUPPORTED_BLEND_MODES)}"
            )

        # Composite onto canvas
        if layer_image.mode == "RGBA":
            if mode == "normal":
                canvas.alpha_composite(layer_image, (x, y))
            else:
                temp = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
                temp.paste(layer_image, (x, y))
                canvas = _blend_layer(canvas, temp, mode)
        else:
            canvas.paste(layer_image, (x, y))

        # Record placement by id for relative() lookups
        if layer_id:
            placed[layer_id] = (x, y, image.width, image.height)

    return ImageArtifact(canvas)


def _blend_channel(base: int, blend: int, mode: str) -> int:
    """Apply blend formula to a single channel (0-255). Returns 0-255."""
    b = base / 255.0
    s = blend / 255.0
    if mode == "multiply":
        out = b * s
    elif mode == "screen":
        out = 1.0 - (1.0 - b) * (1.0 - s)
    elif mode == "overlay":
        out = 2.0 * b * s if b < 0.5 else 1.0 - 2.0 * (1.0 - b) * (1.0 - s)
    elif mode == "darken":
        out = min(b, s)
    elif mode == "lighten":
        out = max(b, s)
    elif mode == "add":
        out = min(1.0, b + s)
    else:
        out = s  # fallback
    return max(0, min(255, int(round(out * 255))))


def _blend_layer(base: Image.Image, blend: Image.Image, mode: str) -> Image.Image:
    """Composite blend over base using the given blend mode. Both must be RGBA, same size."""
    if base.size != blend.size:
        raise ValueError(
            f"base and blend must have same size, got {base.size} and {blend.size}"
        )
    w, h = base.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    base_px = base.load()
    blend_px = blend.load()
    out_px = out.load()
    for py in range(h):
        for px in range(w):
            br, bg, bb, ba = base_px[px, py]
            sr, sg, sb, sa = blend_px[px, py]
            if sa == 0:
                out_px[px, py] = (br, bg, bb, ba)
                continue
            if sa == 255 and ba == 0:
                out_px[px, py] = (sr, sg, sb, sa)
                continue
            # Blend RGB using mode
            r = _blend_channel(br, sr, mode)
            g = _blend_channel(bg, sg, mode)
            b_val = _blend_channel(bb, sb, mode)
            # Alpha: over composite
            sa_n = sa / 255.0
            ba_n = ba / 255.0
            a_out = sa_n + ba_n * (1.0 - sa_n)
            if a_out <= 0:
                out_px[px, py] = (0, 0, 0, 0)
                continue
            # Premultiplied-style mix: result = blend * sa + base * (1-sa) for color
            # Then un-premultiply by a_out for final alpha
            r_out = int(round((r * sa_n + br * (1 - sa_n))))
            g_out = int(round((g * sa_n + bg * (1 - sa_n))))
            b_out = int(round((b_val * sa_n + bb * (1 - sa_n))))
            a_out_int = max(0, min(255, int(round(a_out * 255))))
            out_px[px, py] = (r_out, g_out, b_out, a_out_int)
    return out


def _resolve_position(
    anchor: dict[str, Any],
    image: ImageArtifact,
    layer_id: str | None,
    placed: dict[str, tuple[int, int, int, int]],
    canvas_width: int,
    canvas_height: int,
) -> tuple[int, int]:
    """Resolve layer position from anchor spec.

    Args:
        anchor: Anchor specification dict (from absolute() or relative())
        image: ImageArtifact for this layer
        layer_id: Optional layer ID (for error messages)
        placed: Dict of placed layers by id -> (x, y, width, height)
        canvas_width: Canvas width
        canvas_height: Canvas height

    Returns:
        (x, y) pixel coordinates.

    Raises:
        ValueError: If anchor type is unknown or relative() parent not found.
    """
    anchor_type = anchor.get("type")

    if anchor_type == "absolute":
        x = _to_int(anchor.get("x", 0))
        y = _to_int(anchor.get("y", 0))
        return (x, y)

    elif anchor_type == "relative":
        parent_id = anchor.get("parent")
        if not isinstance(parent_id, str):
            raise ValueError(
                f"Layer {layer_id or 'unknown'}: relative() anchor must have 'parent' as string"
            )

        if parent_id not in placed:
            raise ValueError(
                f"Layer {layer_id or 'unknown'}: references parent '{parent_id}' which hasn't been placed yet. "
                f"Make sure the parent layer has an 'id' field and appears earlier in the layers list."
            )

        align_str = anchor.get("align", "c@c")
        x_offset = _to_int(anchor.get("x", 0))
        y_offset = _to_int(anchor.get("y", 0))

        # Get parent bounds
        parent_x, parent_y, parent_w, parent_h = placed[parent_id]

        # Get self bounds
        self_w = image.width
        self_h = image.height

        # Parse alignment
        self_align, parent_align = _parse_alignment(align_str)

        # Calculate position
        x = _align_position(
            self_align[0], parent_align[0], self_w, parent_w, parent_x, x_offset
        )
        y = _align_position(
            self_align[1], parent_align[1], self_h, parent_h, parent_y, y_offset
        )

        return (x, y)

    else:
        raise ValueError(f"Unknown anchor type: {anchor_type}")


def _parse_alignment(align_str: str) -> tuple[tuple[str, str], tuple[str, str]]:
    """Parse alignment string into self and parent alignments.

    Format: "self@parent" (e.g., "c@c", "se@es") where:
    - @ separates self and parent
    - Single char applies to both axes (e.g., "c" means "cc")
    - Two chars: first is x-axis, second is y-axis

    Returns:
        ((self_x, self_y), (parent_x, parent_y))

    Raises:
        ValueError: If alignment string format is invalid.
    """
    if "@" not in align_str:
        raise ValueError(f"Alignment string must use '@' separator, got '{align_str}'")

    parts = align_str.split("@")
    if len(parts) != 2:
        raise ValueError(f"Alignment string must be 'self@parent', got '{align_str}'")

    self_str = parts[0].strip()
    parent_str = parts[1].strip()

    # Parse self alignment
    if len(self_str) == 1:
        self_align = (self_str, self_str)  # Apply to both axes
    elif len(self_str) == 2:
        self_align = (self_str[0], self_str[1])
    else:
        raise ValueError(f"Self alignment must be 1-2 chars, got '{self_str}'")

    # Parse parent alignment
    if len(parent_str) == 1:
        parent_align = (parent_str, parent_str)  # Apply to both axes
    elif len(parent_str) == 2:
        parent_align = (parent_str[0], parent_str[1])
    else:
        raise ValueError(f"Parent alignment must be 1-2 chars, got '{parent_str}'")

    # Validate chars
    for char in self_align + parent_align:
        if char not in ("s", "c", "e"):
            raise ValueError(f"Alignment char must be 's', 'c', or 'e', got '{char}'")

    return (self_align, parent_align)


def _align_position(
    self_align: str,
    parent_align: str,
    self_size: int,
    parent_size: int,
    parent_pos: int,
    offset: int,
) -> int:
    """Calculate position for one axis based on alignment.

    Args:
        self_align: 's', 'c', or 'e' (self alignment point)
        parent_align: 's', 'c', or 'e' (parent alignment point)
        self_size: Size of self on this axis
        parent_size: Size of parent on this axis
        parent_pos: Position of parent on this axis
        offset: Additional offset

    Returns:
        Position coordinate for self on this axis.
    """
    # Calculate parent alignment point
    if parent_align == "s":
        parent_point = parent_pos
    elif parent_align == "c":
        parent_point = parent_pos + parent_size // 2
    elif parent_align == "e":
        parent_point = parent_pos + parent_size
    else:
        raise ValueError(f"Invalid parent_align: {parent_align}")

    # Calculate self position so self_align point aligns with parent_point
    if self_align == "s":
        self_pos = parent_point
    elif self_align == "c":
        self_pos = parent_point - self_size // 2
    elif self_align == "e":
        self_pos = parent_point - self_size
    else:
        raise ValueError(f"Invalid self_align: {self_align}")

    return self_pos + offset


def _to_int(value: Any) -> int:
    """Convert value to int, handling Decimal, int, str."""
    if isinstance(value, Decimal):
        return int(value)
    elif isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(float(value))  # Handle "10.5" -> 10
        except ValueError:
            raise ValueError(f"Cannot convert '{value}' to int")
    elif isinstance(value, float):
        return int(value)
    else:
        raise ValueError(f"Cannot convert {type(value)} to int")
