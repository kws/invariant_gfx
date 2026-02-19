#!/usr/bin/env python3
"""Example: Thermometer Button Pipeline

This example demonstrates the full op chain from the architecture specification:
- gfx:resolve_resource (icon loading)
- gfx:render_svg (SVG rasterization)
- gfx:render_text (text rendering)
- gfx:create_solid (background)
- gfx:layout (vertical arrangement)
- gfx:composite (final composition)

Usage:
    poetry run python examples/thermometer_button.py
    poetry run python examples/thermometer_button.py --size 72 --icon lucide:thermometer --temperature "22.5C" --font Geneva --output output/thermo.png
"""

import argparse
from decimal import Decimal
from pathlib import Path

from invariant import Executor, Node
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import absolute, relative


def create_thermometer_graph(
    size: int, icon_name: str, temperature: str, font: str
) -> dict:
    """Create the thermometer button graph.

    Args:
        size: Canvas size (width and height in pixels)
        icon_name: Icon resource name (e.g., "lucide:thermometer")
        temperature: Temperature text to display
        font: Font family name (e.g., "Geneva")

    Returns:
        Graph dictionary.
    """
    graph = {
        # Resolve icon resource
        "icon_blob": Node(
            op_name="gfx:resolve_resource",
            params={
                "name": icon_name,
            },
            deps=[],
        ),
        # Render icon SVG to raster
        "icon": Node(
            op_name="gfx:render_svg",
            params={
                "svg_content": "${icon_blob}",
                "width": Decimal("50"),
                "height": Decimal("50"),
            },
            deps=["icon_blob"],
        ),
        # Render temperature text
        "text": Node(
            op_name="gfx:render_text",
            params={
                "text": temperature,
                "font": font,
                "size": Decimal("12"),
                "color": (255, 255, 255, 255),  # White RGBA
            },
            deps=[],
        ),
        # Create background
        "background": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal(str(size)), Decimal(str(size))),
                "color": (40, 40, 40, 255),  # Dark gray RGBA
            },
            deps=[],
        ),
        # Layout icon and text vertically
        "content": Node(
            op_name="gfx:layout",
            params={
                "direction": "column",
                "align": "c",
                "gap": Decimal("5"),
                "items": ["icon", "text"],
            },
            deps=["icon", "text"],
        ),
        # Composite onto background
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": {
                    "background": absolute(0, 0),  # First layer defines canvas
                    "content": relative("background", "c,c"),  # Center on background
                },
            },
            deps=["background", "content"],
        ),
    }

    return graph


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a thermometer button image using invariant_gfx pipeline"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=72,
        help="Canvas size in pixels (default: 72)",
    )
    parser.add_argument(
        "--icon",
        type=str,
        default="lucide:thermometer",
        help='Icon resource name (default: "lucide:thermometer")',
    )
    parser.add_argument(
        "--temperature",
        type=str,
        default="22.5°C",
        help='Temperature text to display (default: "22.5°C")',
    )
    parser.add_argument(
        "--font",
        type=str,
        default="Geneva",
        help='Font family name (default: "Geneva")',
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/thermo.png",
        help="Output PNG file path (default: output/thermo.png)",
    )

    args = parser.parse_args()

    # Create graph
    graph = create_thermometer_graph(
        size=args.size,
        icon_name=args.icon,
        temperature=args.temperature,
        font=args.font,
    )

    # Setup executor
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    # Execute graph
    print("Generating thermometer button...")
    print(f"  Size: {args.size}x{args.size}")
    print(f"  Icon: {args.icon}")
    print(f"  Temperature: {args.temperature}")
    print(f"  Font: {args.font}")

    results = executor.execute(graph)

    # Save output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_image = results["final"].image
    final_image.save(output_path, format="PNG")

    print(f"\n✓ Saved to: {output_path}")
    print(f"  Dimensions: {final_image.width}x{final_image.height}")
    print(f"  Mode: {final_image.mode}")


if __name__ == "__main__":
    main()
