#!/usr/bin/env python3
"""Example: Quick Start - Proportional Sizing

This example demonstrates proportional scaling with Decimal arithmetic:
- Graph designed at 72px reference size
- Font size scales proportionally using Decimal expressions
- Renders at different sizes (72x72 and 144x144)

Usage:
    uv run python examples/quick_start.py
"""

import argparse
from decimal import Decimal
from pathlib import Path

from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import relative

from example_fonts import resolve_example_font


def create_graph(size: int, font: str) -> dict:
    """Create the graph for a given size.

    Args:
        size: Canvas size (width and height in pixels)
        font: Font family name (must be resolvable by JustMyType)

    Returns:
        Graph dictionary.
    """
    # Calculate proportional font size (14pt at 72px reference)
    font_size = Decimal(str(size)) * Decimal("14") / Decimal("72")

    graph = {
        # Render text with proportional sizing
        "text": Node(
            op_name="gfx:render_text",
            params={
                "text": "Hello",
                "font": font,
                "size": int(font_size),
                "color": (255, 255, 255, 255),  # White RGBA
            },
            deps=[],
        ),
        # Create background
        "background": Node(
            op_name="gfx:create_solid",
            params={
                "size": (size, size),
                "color": (40, 40, 40, 255),  # Dark gray RGBA
            },
            deps=[],
        ),
        # Composite: center text on background
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {
                        "image": ref("background"),
                        "id": "background",
                    },
                    {
                        "image": ref("text"),
                        "anchor": relative("background", "c@c"),
                        "id": "text",
                    },
                ],
            },
            deps=["background", "text"],
        ),
    }

    return graph


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a simple text-on-background image using Invariant GFX pipeline"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=72,
        help="Canvas size in pixels (default: 72)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/quick_start.png",
        help="Output PNG file path (default: output/quick_start.png)",
    )

    args = parser.parse_args()

    font = resolve_example_font()

    # Create graph
    graph = create_graph(args.size, font)

    # Setup executor
    registry = OpRegistry()
    register_core_ops(registry)

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    # Execute graph
    print("Generating image...")
    print(f"  Size: {args.size}x{args.size}")
    print(f"  Font: {font}")
    font_size = Decimal(str(args.size)) * Decimal("14") / Decimal("72")
    print(f"  Font size: {font_size}pt (scaled from 14pt at 72px reference)")

    results = executor.execute(graph)

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
