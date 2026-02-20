"""gfx:layout operation - content-sized arrangement engine (row/column flow)."""

from decimal import Decimal

from PIL import Image

from invariant.protocol import ICacheable
from invariant_gfx.artifacts import ImageArtifact


def layout(
    direction: str,
    align: str,
    gap: Decimal | int | str,
    items: list[ImageArtifact],
) -> ICacheable:
    """Arrange items in a flow (row or column) with content-sized output.

    Args:
        direction: "row" or "column" (main axis flow direction)
        align: "s", "c", or "e" (cross-axis alignment)
        gap: Decimal | int | str (spacing between items in pixels)
        items: list[ImageArtifact] (ordered list of images to arrange)

    Returns:
        ImageArtifact sized to the tight bounding box of arranged items (RGBA mode).

    Raises:
        ValueError: If direction/align values are invalid, gap is negative, or items is empty.
    """
    # Validate direction
    if direction not in ("row", "column"):
        raise ValueError(f"direction must be 'row' or 'column', got '{direction}'")

    # Validate align
    if align not in ("s", "c", "e"):
        raise ValueError(f"align must be 's', 'c', or 'e', got '{align}'")

    # Convert gap to int
    if isinstance(gap, Decimal):
        gap_int = int(gap)
    elif isinstance(gap, (int, str)):
        gap_int = int(gap)
    else:
        raise ValueError(f"gap must be Decimal, int, or str, got {type(gap)}")

    if gap_int < 0:
        raise ValueError(f"gap must be non-negative, got {gap_int}")

    # Validate items
    if not isinstance(items, list):
        raise ValueError(f"items must be a list, got {type(items)}")

    if len(items) == 0:
        raise ValueError("items must contain at least one item")

    # Validate all items are ImageArtifact
    for i, item in enumerate(items):
        if not isinstance(item, ImageArtifact):
            raise ValueError(f"items[{i}] must be ImageArtifact, got {type(item)}")

    # Calculate layout dimensions
    if direction == "row":
        # Main axis: horizontal
        # Width = sum of item widths + gaps between items
        total_width = sum(item.width for item in items) + gap_int * (len(items) - 1)
        # Height = max of item heights
        total_height = max(item.height for item in items) if items else 0
    else:  # column
        # Main axis: vertical
        # Width = max of item widths
        total_width = max(item.width for item in items) if items else 0
        # Height = sum of item heights + gaps between items
        total_height = sum(item.height for item in items) + gap_int * (len(items) - 1)

    if total_width <= 0 or total_height <= 0:
        raise ValueError(
            f"Layout dimensions invalid: {total_width}x{total_height}. "
            f"All items must have positive dimensions."
        )

    # Create canvas
    canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

    # Place items
    if direction == "row":
        # Horizontal arrangement
        x = 0
        for item in items:
            # Calculate y position based on cross-axis alignment
            if align == "s":
                y = 0
            elif align == "c":
                y = (total_height - item.height) // 2
            else:  # align == "e"
                y = total_height - item.height

            # Paste item
            canvas.paste(item.image, (x, y), item.image)

            # Move to next position
            x += item.width + gap_int

    else:  # column
        # Vertical arrangement
        y = 0
        for item in items:
            # Calculate x position based on cross-axis alignment
            if align == "s":
                x = 0
            elif align == "c":
                x = (total_width - item.width) // 2
            else:  # align == "e"
                x = total_width - item.width

            # Paste item
            canvas.paste(item.image, (x, y), item.image)

            # Move to next position
            y += item.height + gap_int

    return ImageArtifact(canvas)
