#!/usr/bin/env python3
"""Example: Shapes Showcase — Composite of All Shape Primitives

This example demonstrates the invariant_gfx.shapes library by rendering
each shape (rect, rounded_rect, circle, ellipse, line, polygon, arc,
diamond, parallelogram, hexagon, arrow) and compositing them into a
single image.

Usage:
    uv run python examples/shapes_showcase.py
    uv run python examples/shapes_showcase.py --cell-size 56 --output output/shapes.png
"""

import argparse
from decimal import Decimal
from pathlib import Path

from invariant import Executor, Node, SubGraphNode, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import relative

from example_fonts import resolve_example_font
from invariant_gfx.shapes import (
    arc,
    arrow,
    circle,
    diamond,
    ellipse,
    hexagon,
    line,
    parallelogram,
    polygon,
    rect,
    rounded_rect,
)


def make_shape_cell(
    name: str,
    svg_content: str,
    *,
    cell_size: int,
    label_font_size: int,
    label_color: tuple[int, int, int, int],
    font: str,
) -> SubGraphNode:
    """Return a SubGraphNode that draws the shape, the label text, and layouts them vertically.

    The internal graph: shape (gfx:render_svg) + label (gfx:render_text) → layout (gfx:layout).
    """
    w = Decimal(str(cell_size))
    h = Decimal(str(cell_size))
    graph: dict[str, Node] = {}
    graph["shape"] = Node(
        op_name="gfx:render_svg",
        params={"svg_content": svg_content, "width": w, "height": h},
        deps=[],
    )
    graph["label"] = Node(
        op_name="gfx:render_text",
        params={
            "text": name,
            "font": font,
            "size": Decimal(str(label_font_size)),
            "color": label_color,
        },
        deps=[],
    )
    graph["cell"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("4"),
            "items": [ref("shape"), ref("label")],
        },
        deps=["shape", "label"],
    )
    return SubGraphNode(params={}, deps=[], graph=graph, output="cell")


def _shape_specs(cs: int, colors: list, stroke: tuple):
    """Return [(name, svg_content), ...] for each shape."""
    return [
        ("rect", rect(cs, cs, fill=colors[0])),
        ("rounded_rect", rounded_rect(cs, cs, rx=cs // 6, fill=colors[1])),
        ("circle", circle(cs // 2, cs // 2, cs // 2 - 2, fill=colors[2])),
        ("ellipse", ellipse(cs // 2, cs // 2, cs // 3, cs // 4, fill=colors[3])),
        ("line", line(4, 4, cs - 4, cs - 4, stroke=stroke)),
        (
            "polygon",
            polygon([(cs // 2, 4), (cs - 4, cs - 4), (4, cs - 4)], fill=colors[4]),
        ),
        ("arc", arc(cs // 2, cs // 2, cs // 2 - 4, 0, 270, pie=True, fill=colors[5])),
        ("diamond", diamond(cs, cs, fill=colors[6])),
        ("parallelogram", parallelogram(cs, cs, skew=Decimal("0.2"), fill=colors[7])),
        ("hexagon", hexagon(cs, cs, flat_top=True, fill=colors[8])),
        (
            "arrow",
            arrow(
                8,
                cs // 2,
                cs - 8,
                cs // 2,
                stroke=stroke,
                stroke_width=2,
                head_size=cs // 6,
            ),
        ),
    ]


def create_shapes_showcase_graph(cell_size: int, font: str) -> dict:
    """Create the shapes showcase graph."""
    colors = [
        (30, 100, 180, 255),
        (0, 140, 90, 255),
        (200, 0, 50, 255),
        (230, 120, 0, 255),
        (100, 0, 120, 255),
        (0, 150, 220, 255),
        (220, 180, 0, 255),
        (220, 80, 50, 255),
        (120, 80, 200, 255),
    ]
    stroke = (20, 20, 20, 255)
    label_color = (30, 30, 30, 255)
    label_font_size = max(9, cell_size // 5)

    graph: dict = {}
    cells: list[str] = []
    for name, svg_content in _shape_specs(cell_size, colors, stroke):
        cell_id = f"cell_{name}"
        graph[cell_id] = make_shape_cell(
            name,
            svg_content,
            cell_size=cell_size,
            label_font_size=label_font_size,
            label_color=label_color,
            font=font,
        )
        cells.append(cell_id)
    rows_layout = [cells[:5], cells[5:10], cells[10:]]  # 5 + 5 + 1

    for i, row_cells in enumerate(rows_layout):
        graph[f"row{i + 1}"] = Node(
            op_name="gfx:layout",
            params={
                "direction": "row",
                "align": "c",
                "gap": Decimal("8"),
                "items": [ref(c) for c in row_cells],
            },
            deps=row_cells,
        )

    graph["shapes_layout"] = Node(
        op_name="gfx:layout",
        params={
            "direction": "column",
            "align": "c",
            "gap": Decimal("12"),
            "items": [ref("row1"), ref("row2"), ref("row3")],
        },
        deps=["row1", "row2", "row3"],
    )

    cell_with_label_h = cell_size + label_font_size + 8
    pad = 24
    bg_w = 5 * cell_size + 4 * 8 + 2 * pad
    bg_h = 3 * cell_with_label_h + 2 * 12 + 2 * pad
    graph["background"] = Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal(str(bg_w)), Decimal(str(bg_h))),
            "color": (255, 255, 255, 255),
        },
        deps=[],
    )
    graph["final"] = Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("background"), "id": "background"},
                {
                    "image": ref("shapes_layout"),
                    "anchor": relative("background", "c@c"),
                    "id": "shapes_layout",
                },
            ],
        },
        deps=["background", "shapes_layout"],
    )
    return graph


def main():
    parser = argparse.ArgumentParser(
        description="Generate a composite image of all invariant_gfx shapes"
    )
    parser.add_argument(
        "--cell-size", type=int, default=96, help="Size of each shape cell in pixels"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/shapes_showcase.png",
        help="Output PNG path",
    )
    args = parser.parse_args()

    font = resolve_example_font()
    graph = create_shapes_showcase_graph(args.cell_size, font)
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)
    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    print("Generating shapes showcase...")
    print(f"  Cell size: {args.cell_size}x{args.cell_size}")
    print("  Shapes: rect, rounded_rect, circle, ellipse, line,")
    print("          polygon, arc, diamond, parallelogram, hexagon, arrow")

    results = executor.execute(graph)
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
