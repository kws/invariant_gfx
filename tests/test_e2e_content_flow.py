"""End-to-end tests for content flow layout pipeline.

This test implements Use Case 2 from Section 10.3 of the architecture specification.
Tests gfx:layout in both row and column modes with differently-sized blocks.
"""

from decimal import Decimal

from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore
from invariant_gfx import register_core_ops


def test_content_flow_row_layout():
    """Test row layout pipeline from architecture spec Section 10.3.

    This test verifies:
    - gfx:layout row mode with three differently-sized blocks
    - Output dimensions: width = 70 (20+5+20+5+20), height = 30 (tallest)
    - Pixel colors at expected positions confirm arrangement order

    See docs/architecture.md Section 10.3 for the complete specification.
    """
    # Register graphics ops
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    # Define the graph
    graph = {
        # Create three differently-sized colored blocks
        "block_a": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("30")),
                "color": (200, 0, 0, 255),  # Red RGBA
            },
            deps=[],
        ),
        "block_b": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("20")),
                "color": (0, 200, 0, 255),  # Green RGBA
            },
            deps=[],
        ),
        "block_c": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("10")),
                "color": (0, 0, 200, 255),  # Blue RGBA
            },
            deps=[],
        ),
        # Row layout: horizontal arrangement
        "row_layout": Node(
            op_name="gfx:layout",
            params={
                "direction": "row",
                "align": "c",  # Center on cross-axis
                "gap": Decimal("5"),
                "items": [ref("block_a"), ref("block_b"), ref("block_c")],
            },
            deps=["block_a", "block_b", "block_c"],
        ),
    }

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)
    results = executor.execute(graph, ["row_layout"])

    # Verify row layout dimensions
    # Width = 20 + 5 + 20 + 5 + 20 = 70
    # Height = max(30, 20, 10) = 30
    assert results["row_layout"].width == 70
    assert results["row_layout"].height == 30

    # Verify pixel colors at expected positions
    row_image = results["row_layout"].image
    # First block (red) at left edge, centered vertically
    # Block is 20x30, centered at y=0 (since it's tallest), so y=15 is center
    assert row_image.getpixel((10, 15)) == (200, 0, 0, 255)
    # Second block (green) in middle, centered vertically
    # Block is 20x20, centered at y=5 (since max height is 30), so y=15 is center
    assert row_image.getpixel((35, 10)) == (0, 200, 0, 255)
    # Third block (blue) at right edge, centered vertically
    # Block is 20x10, at x=50 (20+5+20+5), centered at y=10.
    assert row_image.getpixel((50, 10)) == (0, 0, 200, 255)


def test_content_flow_column_layout():
    """Test column layout pipeline from architecture spec Section 10.3.

    This test verifies:
    - gfx:layout column mode with three differently-sized blocks
    - Output dimensions: width = 20 (widest), height = 70 (30+5+20+5+10)
    - Pixel colors at expected positions confirm arrangement order

    See docs/architecture.md Section 10.3 for the complete specification.
    """
    # Register graphics ops
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    # Define the graph
    graph = {
        # Create three differently-sized colored blocks
        "block_a": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("30")),
                "color": (200, 0, 0, 255),  # Red RGBA
            },
            deps=[],
        ),
        "block_b": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("20")),
                "color": (0, 200, 0, 255),  # Green RGBA
            },
            deps=[],
        ),
        "block_c": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("10")),
                "color": (0, 0, 200, 255),  # Blue RGBA
            },
            deps=[],
        ),
        # Column layout: vertical arrangement
        "col_layout": Node(
            op_name="gfx:layout",
            params={
                "direction": "column",
                "align": "c",  # Center on cross-axis
                "gap": Decimal("5"),
                "items": [ref("block_a"), ref("block_b"), ref("block_c")],
            },
            deps=["block_a", "block_b", "block_c"],
        ),
    }

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)
    results = executor.execute(graph, ["col_layout"])

    # Verify column layout dimensions
    # Width = max(20, 20, 20) = 20
    # Height = 30 + 5 + 20 + 5 + 10 = 70
    assert results["col_layout"].width == 20
    assert results["col_layout"].height == 70

    # Verify pixel colors at expected positions
    col_image = results["col_layout"].image
    # First block (red) at top, centered horizontally
    assert col_image.getpixel((10, 15)) == (200, 0, 0, 255)
    # Second block (green) in middle, centered horizontally
    assert col_image.getpixel((10, 42)) == (0, 200, 0, 255)
    # Third block (blue) at bottom, centered horizontally
    assert col_image.getpixel((10, 65)) == (0, 0, 200, 255)


def test_content_flow_fan_out():
    """Test that same source blocks can feed multiple layout nodes (fan-out pattern)."""
    # Register graphics ops
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    # Define the graph with fan-out
    graph = {
        # Create three differently-sized colored blocks
        "block_a": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("30")),
                "color": (200, 0, 0, 255),  # Red RGBA
            },
            deps=[],
        ),
        "block_b": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("20")),
                "color": (0, 200, 0, 255),  # Green RGBA
            },
            deps=[],
        ),
        "block_c": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("20"), Decimal("10")),
                "color": (0, 0, 200, 255),  # Blue RGBA
            },
            deps=[],
        ),
        # Row layout: horizontal arrangement
        "row_layout": Node(
            op_name="gfx:layout",
            params={
                "direction": "row",
                "align": "c",
                "gap": Decimal("5"),
                "items": [ref("block_a"), ref("block_b"), ref("block_c")],
            },
            deps=["block_a", "block_b", "block_c"],
        ),
        # Column layout: vertical arrangement (fan-out from same sources)
        "col_layout": Node(
            op_name="gfx:layout",
            params={
                "direction": "column",
                "align": "c",
                "gap": Decimal("5"),
                "items": [ref("block_a"), ref("block_b"), ref("block_c")],
            },
            deps=["block_a", "block_b", "block_c"],
        ),
    }

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)
    results = executor.execute(graph, ["row_layout", "col_layout"])

    # Verify both layouts produce correct outputs
    # Row layout
    assert results["row_layout"].width == 70
    assert results["row_layout"].height == 30

    # Column layout
    assert results["col_layout"].width == 20
    assert results["col_layout"].height == 70

    # Verify pixel colors in both layouts
    row_image = results["row_layout"].image
    assert row_image.getpixel((10, 15)) == (200, 0, 0, 255)  # Red
    assert row_image.getpixel((35, 10)) == (0, 200, 0, 255)  # Green
    assert row_image.getpixel((50, 10)) == (0, 0, 200, 255)  # Blue

    col_image = results["col_layout"].image
    assert col_image.getpixel((10, 15)) == (200, 0, 0, 255)  # Red
    assert col_image.getpixel((10, 42)) == (0, 200, 0, 255)  # Green
    assert col_image.getpixel((10, 65)) == (0, 0, 200, 255)  # Blue
