#!/usr/bin/env python3
"""Example: Color Dashboard Pipeline

This example demonstrates a multi-cell dashboard with labeled colored blocks.
Exercises layout nesting and text rendering.

Usage:
    uv run python examples/color_dashboard.py
    uv run python examples/color_dashboard.py \
      --items "CPU:75:red,MEM:42:green,DISK:91:blue" \
      --cell-size 80 \
      --output output/dashboard.png
"""

import argparse
from decimal import Decimal
from pathlib import Path

from example_fonts import resolve_example_font
from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore
from invariant_gfx import register_core_ops
from invariant_gfx.anchors import relative

# Color mapping
COLOR_MAP = {
    "red": (200, 0, 0, 255),
    "green": (0, 200, 0, 255),
    "blue": (0, 0, 200, 255),
    "yellow": (200, 200, 0, 255),
    "orange": (255, 165, 0, 255),
    "purple": (128, 0, 128, 255),
    "gray": (128, 128, 128, 255),
    "darkgray": (40, 40, 40, 255),
}


def parse_items(items_str: str) -> list[tuple[str, int, str]]:
    """Parse items string into list of (label, value, color) tuples.

    Format: "LABEL:VALUE:COLOR,LABEL:VALUE:COLOR,..."

    Args:
        items_str: Comma-separated items string

    Returns:
        List of (label, value, color) tuples.
    """
    items = []
    for item_str in items_str.split(","):
        parts = item_str.split(":")
        if len(parts) != 3:
            raise ValueError(
                f"Invalid item format: {item_str}. Expected LABEL:VALUE:COLOR"
            )
        label, value_str, color = parts
        try:
            value = int(value_str)
        except ValueError as exc:
            raise ValueError(
                f"Invalid value in item: {item_str}. Value must be integer"
            ) from exc
        if color not in COLOR_MAP:
            raise ValueError(
                f"Unknown color: {color}. Available: {list(COLOR_MAP.keys())}"
            )
        items.append((label, value, color))
    return items


def create_dashboard_graph(
    items: list[tuple[str, int, str]], cell_size: int, font: str
) -> dict:
    """Create the dashboard graph.

    Args:
        items: List of (label, value, color) tuples
        cell_size: Size of each cell in pixels
        font: Font family name

    Returns:
        Graph dictionary.
    """
    graph = {}

    # Create cells for each item
    cell_nodes = []
    for i, (label, value, color) in enumerate(items):
        cell_id = f"cell_{i}"

        # Create colored block (proportional to value, max 100)
        block_height = int(cell_size * (value / 100.0))
        block_id = f"{cell_id}_block"
        graph[block_id] = Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal(str(cell_size)), Decimal(str(block_height))),
                "color": COLOR_MAP[color],
            },
            deps=[],
        )

        # Render label text
        label_id = f"{cell_id}_label"
        graph[label_id] = Node(
            op_name="gfx:render_text",
            params={
                "text": label,
                "font": font,
                "size": Decimal("14"),
                "color": (255, 255, 255, 255),  # White
            },
            deps=[],
        )

        # Render value text
        value_id = f"{cell_id}_value"
        graph[value_id] = Node(
            op_name="gfx:render_text",
            params={
                "text": str(value),
                "font": font,
                "size": Decimal("18"),
                "color": (255, 255, 255, 255),  # White
            },
            deps=[],
        )

        # Layout text elements (label + value) vertically
        text_group_id = f"{cell_id}_text"
        graph[text_group_id] = Node(
            op_name="gfx:layout",
            params={
                "direction": "column",
                "align": "c",
                "gap": Decimal("5"),
                "items": [ref(label_id), ref(value_id)],
            },
            deps=[label_id, value_id],
        )

        # Create cell background
        cell_bg_id = f"{cell_id}_bg"
        graph[cell_bg_id] = Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal(str(cell_size + 20)), Decimal(str(cell_size + 40))),
                "color": (60, 60, 60, 255),  # Dark gray background
            },
            deps=[],
        )

        # Composite cell: text at top-center, bar at bottom-center
        # Use two nested composites to avoid chain constraint issues

        # Composite 1: cell background + colored block at bottom-center
        cell_with_block_id = f"{cell_id}_with_block"
        graph[cell_with_block_id] = Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {
                        "image": ref(cell_bg_id),
                        "id": cell_bg_id,
                    },
                    {
                        "image": ref(block_id),
                        "anchor": relative(cell_bg_id, "ce@ce", y=-10),
                        "id": block_id,
                    },
                ],
            },
            deps=[cell_bg_id, block_id],
        )

        # Composite 2: result of composite 1 + text group at top-center
        graph[cell_id] = Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {
                        "image": ref(cell_with_block_id),
                        "id": cell_with_block_id,
                    },
                    {
                        "image": ref(text_group_id),
                        "anchor": relative(cell_with_block_id, "cs@cs", y=10),
                        "id": text_group_id,
                    },
                ],
            },
            deps=[cell_with_block_id, text_group_id],
        )

        cell_nodes.append(cell_id)

    # Layout all cells horizontally
    graph["dashboard"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "row",
            "align": "c",
            "gap": Decimal("10"),
            "items": [ref(node_id) for node_id in cell_nodes],
        },
        deps=cell_nodes,
    )

    # Create final background
    # Calculate approximate width (will be adjusted by layout)
    estimated_width = len(items) * (cell_size + 20) + (len(items) - 1) * 10
    graph["final_bg"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(estimated_width + 40)), Decimal(str(cell_size + 80))),
            "color": (30, 30, 30, 255),  # Very dark gray
        },
        deps=[],
    )

    # Final composite
    graph["final"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {
                    "image": ref("final_bg"),
                    "id": "final_bg",
                },
                {
                    "image": ref("dashboard"),
                    "anchor": relative("final_bg", "c@c"),
                    "id": "dashboard",
                },
            ],
        },
        deps=["final_bg", "dashboard"],
    )

    return graph


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a color dashboard image using Invariant GFX pipeline"
    )
    parser.add_argument(
        "--items",
        type=str,
        default="CPU:75:red,MEM:42:green,DISK:91:blue",
        help=(
            'Comma-separated items in format "LABEL:VALUE:COLOR" '
            '(e.g., "CPU:75:red,MEM:42:green")'
        ),
    )
    parser.add_argument(
        "--cell-size",
        type=int,
        default=80,
        help="Size of each cell in pixels (default: 80)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/dashboard.png",
        help="Output PNG file path (default: output/dashboard.png)",
    )

    args = parser.parse_args()

    font = resolve_example_font()

    # Parse items
    try:
        items = parse_items(args.items)
    except ValueError as e:
        print(f"Error parsing items: {e}")
        return 1

    if not items:
        print("Error: No items provided")
        return 1

    # Create graph
    graph = create_dashboard_graph(items, args.cell_size, font)

    # Setup executor
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    # Execute graph
    print("Generating color dashboard...")
    print(f"  Items: {len(items)}")
    print(f"  Cell size: {args.cell_size}x{args.cell_size}")
    for label, value, color in items:
        print(f"    - {label}: {value}% ({color})")

    results = executor.execute(graph, ["final"])

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_image = results["final"].image
    final_image.save(output_path, format="PNG")

    print(f"\n✓ Saved to: {output_path}")
    print(f"  Dimensions: {final_image.width}x{final_image.height}")
    print(f"  Mode: {final_image.mode}")

    return 0


if __name__ == "__main__":
    exit(main())
