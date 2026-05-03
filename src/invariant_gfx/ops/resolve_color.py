"""gfx:resolve_color operation - resolves color specs to RGBA tuples."""

from typing import Any

from PIL import ImageColor


def _validate_channels(
    channels: tuple[Any, ...], source: Any
) -> tuple[int, int, int, int]:
    if len(channels) == 3:
        channels = (*channels, 255)
    elif len(channels) != 4:
        raise ValueError(
            f"color must have 3 or 4 channels, got {len(channels)} from {source!r}"
        )

    if not all(
        isinstance(channel, int) and 0 <= channel <= 255
        for channel in channels
    ):
        raise ValueError(f"color channels must be int in range 0-255, got {source!r}")

    return channels


def resolve_color(
    color: str | tuple[int, ...] | list[int],
) -> tuple[int, int, int, int]:
    """Resolve a color specification to an RGBA tuple.

    Args:
        color: CSS-style color string supported by Pillow, or an RGB/RGBA
            tuple/list with integer channels.

    Returns:
        Tuple[int, int, int, int] RGBA channels.

    Raises:
        ValueError: If the color cannot be resolved.
    """
    if isinstance(color, str):
        if color.lower() == "transparent":
            return (0, 0, 0, 0)
        try:
            return tuple(ImageColor.getcolor(color, "RGBA"))
        except ValueError as e:
            raise ValueError(f"failed to resolve color {color!r}: {e}") from e

    if isinstance(color, (tuple, list)):
        return _validate_channels(tuple(color), color)

    raise ValueError(f"color must be a string, tuple, or list, got {type(color)}")
