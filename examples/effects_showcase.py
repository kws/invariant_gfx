#!/usr/bin/env python3
"""Example: Effects Showcase — Six Effect Recipes

This example demonstrates the invariant_gfx effect recipes (drop_shadow,
outer_stroke, outer_glow, inner_shadow, inner_glow, reflection) by
applying each to a text source and compositing into a grid.

Usage:
    uv run python examples/effects_showcase.py
    uv run python examples/effects_showcase.py \
      --cell-size 80 \
      --output output/effects.png
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
from invariant_gfx.recipes import (
    drop_shadow,
    inner_glow,
    inner_shadow,
    outer_glow,
    outer_stroke,
    reflection,
)


def create_effects_showcase_graph(cell_size: int, font: str) -> dict:
    """Create the effects showcase graph."""
    graph: dict = {}
    text_size = Decimal(str(max(80, cell_size // 3)))
    label_font_size = max(9, cell_size // 6)
    label_color = (40, 40, 40, 255)
    label_color_dark = (220, 220, 220, 255)  # for cells with dark background
    bg_color = (255, 255, 255, 255)

    # Shared text source
    graph["text"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "Hi",
            "font": font,
            "size": text_size,
            "color": (60, 60, 60, 255),
        },
        deps=[],
    )

    # Background for each cell (large enough for effects)
    pad = 40
    bg_size = cell_size + pad

    # 1. Drop shadow
    graph["shadow"] = drop_shadow("text", dx=2, dy=2, sigma=Decimal("3"))
    graph["bg_ds"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(bg_size)), Decimal(str(bg_size))),
            "color": bg_color,
        },
        deps=[],
    )
    graph["effect_ds"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("bg_ds"), "id": "bg"},
                {
                    "image": ref("shadow"),
                    "anchor": relative("bg", "c@c"),
                    "id": "shadow",
                },
                {"image": ref("text"), "anchor": relative("bg", "c@c"), "id": "text"},
            ],
        },
        deps=["bg_ds", "shadow", "text"],
    )
    graph["label_ds"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "drop_shadow",
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color,
        },
        deps=[],
    )
    graph["cell_ds"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("effect_ds"), ref("label_ds")],
        },
        deps=["effect_ds", "label_ds"],
    )

    # 2. Outer stroke
    graph["stroke"] = outer_stroke("text", width=2, color=(0, 0, 0, 255))
    graph["bg_os"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(bg_size)), Decimal(str(bg_size))),
            "color": bg_color,
        },
        deps=[],
    )
    graph["effect_os"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("bg_os"), "id": "bg"},
                {
                    "image": ref("stroke"),
                    "anchor": relative("bg", "c@c"),
                    "id": "stroke",
                },
                {"image": ref("text"), "anchor": relative("bg", "c@c"), "id": "text"},
            ],
        },
        deps=["bg_os", "stroke", "text"],
    )
    graph["label_os"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "outer_stroke",
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color,
        },
        deps=[],
    )
    graph["cell_os"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("effect_os"), ref("label_os")],
        },
        deps=["effect_os", "label_os"],
    )

    # 3. Outer glow (dark bg so glow is visible)
    graph["glow"] = outer_glow("text", sigma=Decimal("5"), color=(255, 200, 0, 200))
    graph["bg_og"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(bg_size)), Decimal(str(bg_size))),
            "color": (30, 30, 30, 255),
        },
        deps=[],
    )
    graph["effect_og"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("bg_og"), "id": "bg"},
                {
                    "image": ref("glow"),
                    "anchor": relative("bg", "c@c"),
                    "id": "glow",
                    "mode": "add",
                },
                {"image": ref("text"), "anchor": relative("bg", "c@c"), "id": "text"},
            ],
        },
        deps=["bg_og", "glow", "text"],
    )
    graph["label_og"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "outer_glow",
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color_dark,
        },
        deps=[],
    )
    graph["cell_og"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("effect_og"), ref("label_og")],
        },
        deps=["effect_og", "label_og"],
    )

    # 4. Inner shadow
    graph["inner_sh"] = inner_shadow("text", dx=1, dy=1, sigma=Decimal("2"))
    graph["bg_is"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(bg_size)), Decimal(str(bg_size))),
            "color": bg_color,
        },
        deps=[],
    )
    graph["effect_is"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("bg_is"), "id": "bg"},
                {"image": ref("text"), "anchor": relative("bg", "c@c"), "id": "text"},
                {
                    "image": ref("inner_sh"),
                    "anchor": relative("text", "c@c"),
                    "id": "inner_shadow",
                    "mode": "multiply",
                },
            ],
        },
        deps=["bg_is", "text", "inner_sh"],
    )
    graph["label_is"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "inner_shadow",
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color,
        },
        deps=[],
    )
    graph["cell_is"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("effect_is"), ref("label_is")],
        },
        deps=["effect_is", "label_is"],
    )

    # 5. Inner glow (dark bg so glow is visible)
    graph["inner_gl"] = inner_glow(
        "text", sigma=Decimal("3"), color=(255, 255, 200, 180)
    )
    graph["bg_ig"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(bg_size)), Decimal(str(bg_size))),
            "color": (30, 30, 30, 255),
        },
        deps=[],
    )
    graph["effect_ig"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("bg_ig"), "id": "bg"},
                {"image": ref("text"), "anchor": relative("bg", "c@c"), "id": "text"},
                {
                    "image": ref("inner_gl"),
                    "anchor": relative("text", "c@c"),
                    "id": "inner_glow",
                    "mode": "add",
                },
            ],
        },
        deps=["bg_ig", "text", "inner_gl"],
    )
    graph["label_ig"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "inner_glow",
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color_dark,
        },
        deps=[],
    )
    graph["cell_ig"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("effect_ig"), ref("label_ig")],
        },
        deps=["effect_ig", "label_ig"],
    )

    # 6. Reflection (centered below text via cs@ce, no horizontal offset)
    # Use crop_to_content so reflection aligns with bottom of glyphs, not padding.
    # gradient_end_pos=0.5: PowerPoint-style fade out halfway through.
    graph["text_tight"] = Node(
        op_name="gfx:crop_to_content",
        params={"image": ref("text")},
        deps=["text"],
    )
    graph["refl"] = reflection(
        "text_tight",
        gap=0,
        gradient_end_pos=Decimal("0.5"),
        squash=Decimal("0.75"),
        skew=Decimal("0.2"),
    )
    # Layout text + reflection to get content dimensions; background sized to fit.
    graph["effect_rf_content"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("0"),
            "items": [ref("text_tight"), ref("refl")],
        },
        deps=["text_tight", "refl"],
    )
    graph["bg_rf"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": [
                "${effect_rf_content.width + " + str(pad) + "}",
                "${effect_rf_content.height + " + str(pad) + "}",
            ],
            "color": bg_color,
        },
        deps=["effect_rf_content"],
    )
    graph["effect_rf"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("bg_rf"), "id": "bg"},
                {
                    "image": ref("effect_rf_content"),
                    "anchor": relative("bg", "c@c"),
                    "id": "content",
                },
            ],
        },
        deps=["bg_rf", "effect_rf_content"],
    )
    graph["label_rf"] = Node(
        op_name="gfx:render_text",
        params={
            "text": "reflection",
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color,
        },
        deps=[],
    )
    graph["cell_rf"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("effect_rf"), ref("label_rf")],
        },
        deps=["effect_rf", "label_rf"],
    )

    # Layout: 2 rows of 3
    graph["row1"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "row",
            "align": "c",
            "gap": Decimal("12"),
            "items": [ref("cell_ds"), ref("cell_os"), ref("cell_og")],
        },
        deps=["cell_ds", "cell_os", "cell_og"],
    )
    graph["row2"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "row",
            "align": "c",
            "gap": Decimal("12"),
            "items": [ref("cell_is"), ref("cell_ig"), ref("cell_rf")],
        },
        deps=["cell_is", "cell_ig", "cell_rf"],
    )
    graph["effects_layout"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("12"),
            "items": [ref("row1"), ref("row2")],
        },
        deps=["row1", "row2"],
    )

    margin = 24
    graph["background"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": [
                f"${{int(effects_layout.width) + 2*{margin}}}",
                f"${{int(effects_layout.height) + 2*{margin}}}",
            ],
            "color": (250, 250, 250, 255),
        },
        deps=["effects_layout"],
    )
    graph["final"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("background"), "id": "background"},
                {
                    "image": ref("effects_layout"),
                    "anchor": relative("background", "c@c"),
                    "id": "effects_layout",
                },
            ],
        },
        deps=["background", "effects_layout"],
    )
    return graph


def main():
    parser = argparse.ArgumentParser(
        description="Generate a composite image of all invariant_gfx effect recipes"
    )
    parser.add_argument(
        "--cell-size", type=int, default=72, help="Size of each effect cell in pixels"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/effects_showcase.png",
        help="Output PNG path",
    )
    args = parser.parse_args()

    font = resolve_example_font()
    graph = create_effects_showcase_graph(args.cell_size, font)
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)
    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    print("Generating effects showcase...")
    print(f"  Cell size: {args.cell_size}x{args.cell_size}")
    print("  Effects: drop_shadow, outer_stroke, outer_glow,")
    print("           inner_shadow, inner_glow, reflection")

    results = executor.execute(graph, ["final"])
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results["final"].image.save(output_path, format="PNG")

    print(f"\n✓ Saved to: {output_path}")
    print(
        f"  Dimensions: {results['final'].image.width}x{results['final'].image.height}"
    )
    print(f"  Mode: {results['final'].image.mode}")
    return 0


if __name__ == "__main__":
    exit(main())
