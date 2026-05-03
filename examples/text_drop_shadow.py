#!/usr/bin/env python3
"""Example: Text with drop shadow on a transparent background.

Renders text, applies the drop_shadow recipe (SubGraphNode), and composites
shadow + text onto a transparent canvas. Useful for testing the effect recipe
and for producing overlay assets (e.g. for Stream Deck or badges).

Usage:
    uv run python examples/text_drop_shadow.py
    uv run python examples/text_drop_shadow.py --text "Hello"
    uv run python examples/text_drop_shadow.py --text "42" --font-size 24 --output output/shadow.png
"""

import argparse
from decimal import Decimal
from pathlib import Path

from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops

from example_fonts import resolve_example_font
from invariant_gfx.anchors import relative
from invariant_gfx.recipes import drop_shadow


def create_graph(
    text: str,
    font: str,
    font_size: int,
    text_color: tuple[int, int, int, int],
    width: int,
    height: int,
    shadow_dx: int,
    shadow_dy: int,
    shadow_sigma: Decimal,
    shadow_color: tuple[int, int, int, int],
) -> dict:
    """Build graph: text, drop_shadow subgraph, transparent background, composite."""
    graph = {
        "text": Node(
            op_name="gfx:render_text",
            params={
                "text": text,
                "font": font,
                "size": font_size,
                "color": text_color,
            },
            deps=[],
        ),
        "shadow": drop_shadow(
            "text",
            dx=shadow_dx,
            dy=shadow_dy,
            sigma=shadow_sigma,
            color=shadow_color,
        ),
        "background": Node(
            op_name="gfx:create_solid",
            params={
                "size": (width, height),
                "color": (0, 0, 0, 0),  # Transparent
            },
            deps=[],
        ),
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {"image": ref("background"), "id": "background"},
                    {
                        "image": ref("shadow"),
                        "anchor": relative("background", "c@c"),
                        "id": "shadow",
                    },
                    {
                        "image": ref("text"),
                        "anchor": relative("background", "c@c"),
                        "id": "text",
                    },
                ],
            },
            deps=["background", "shadow", "text"],
        ),
    }
    return graph


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render text with drop shadow on transparent background"
    )
    parser.add_argument(
        "--text", type=str, default="Drop shadow", help="Text to render"
    )
    parser.add_argument(
        "--font",
        type=str,
        default=None,
        help=(
            "Font family (default: first available; "
            "install 'invariant-gfx[fonts]' to get one)"
        ),
    )
    parser.add_argument("--font-size", type=int, default=24, help="Font size (pt)")
    parser.add_argument(
        "--width",
        type=int,
        default=280,
        help="Canvas width (default 280)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=80,
        help="Canvas height (default 80)",
    )
    parser.add_argument("--shadow-dx", type=int, default=3, help="Shadow offset X")
    parser.add_argument("--shadow-dy", type=int, default=3, help="Shadow offset Y")
    parser.add_argument(
        "--shadow-sigma",
        type=str,
        default="3",
        help="Shadow blur sigma (default 3)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/text_drop_shadow.png",
        help="Output PNG path",
    )
    args = parser.parse_args()

    font = resolve_example_font(args.font)

    text_color = (255, 255, 255, 255)
    shadow_color = (255, 0, 0, 220)  # Red shadow so it's easy to see on transparent
    sigma = Decimal(args.shadow_sigma)

    graph = create_graph(
        text=args.text,
        font=font,
        font_size=args.font_size,
        text_color=text_color,
        width=args.width,
        height=args.height,
        shadow_dx=args.shadow_dx,
        shadow_dy=args.shadow_dy,
        shadow_sigma=sigma,
        shadow_color=shadow_color,
    )

    registry = OpRegistry()
    register_core_ops(registry)
    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    print("Rendering text with drop shadow (transparent background)...")
    print(f"  Text: {args.text!r}  Font: {font}  Size: {args.font_size}pt")
    print(
        f"  Canvas: {args.width}x{args.height}  Shadow: dx={args.shadow_dx} dy={args.shadow_dy} sigma={sigma}"
    )

    results = executor.execute(graph)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    results["final"].image.save(out_path, format="PNG")

    print(f"\nSaved: {out_path}")
    print(
        f"  Size: {results['final'].image.width}x{results['final'].image.height}  Mode: RGBA"
    )
    return 0


if __name__ == "__main__":
    exit(main())
