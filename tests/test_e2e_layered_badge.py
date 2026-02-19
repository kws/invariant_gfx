"""End-to-end tests for layered badge composition pipeline.

This test implements Use Case 1 from Section 10.2 of the architecture specification.
Tests the core composition engine with absolute() and relative() positioning.
"""

from decimal import Decimal

from invariant import Executor, Node
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import absolute, relative


def test_layered_badge_pipeline():
    """Test the layered badge composition pipeline from architecture spec Section 10.2.

    This test verifies:
    - Three-layer composition with absolute() and relative() anchors
    - Output dimensions (72x72)
    - Pixel colors at known coordinates (center, corner, badge region)

    See docs/architecture.md Section 10.2 for the complete specification.
    """
    # Register graphics ops
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    # Define the graph
    graph = {
        # Create three colored rectangles
        "background": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("72"), Decimal("72")),
                "color": (40, 40, 40, 255),  # Dark gray RGBA
            },
            deps=[],
        ),
        "icon_stand_in": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("32"), Decimal("32")),
                "color": (0, 100, 200, 255),  # Blue RGBA
            },
            deps=[],
        ),
        "badge": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("12"), Decimal("12")),
                "color": (200, 0, 0, 255),  # Red RGBA
            },
            deps=[],
        ),
        # Composite: background at origin, icon centered, badge at icon's top-right
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": {
                    "background": absolute(0, 0),  # First layer defines canvas
                    "icon_stand_in": relative(
                        "background", "c,c"
                    ),  # Center on background
                    "badge": relative(
                        "icon_stand_in", "se,se", x=-2, y=2
                    ),  # Top-right of icon, with offset
                },
            },
            deps=["background", "icon_stand_in", "badge"],
        ),
    }

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)
    results = executor.execute(graph)

    # Verify output dimensions
    assert results["final"].width == 72
    assert results["final"].height == 72

    # Verify pixel colors at known coordinates
    final_image = results["final"].image
    # Center pixel should be blue (icon)
    assert final_image.getpixel((36, 36)) == (0, 100, 200, 255)
    # Top-left corner should be dark gray (background)
    assert final_image.getpixel((0, 0)) == (40, 40, 40, 255)
    # Badge region should have red pixels
    # Icon is centered at (36, 36) and is 32x32, so it's from (20, 20) to (52, 52)
    # Badge uses "se,se" alignment: badge's bottom-left (se) aligns with icon's bottom-left (se)
    # Icon's bottom-left (se) is at (20, 52)
    # With offset x=-2, y=2, badge's bottom-left should be at (18, 54)
    # Badge is 12x12, so it extends from (18, 42) to (30, 54)
    # Check a pixel that should definitely be in the badge (center of badge)
    badge_center_x = 18 + 6  # 24
    badge_center_y = 42 + 6  # 48
    assert final_image.getpixel((badge_center_x, badge_center_y)) == (200, 0, 0, 255)


def test_layered_badge_cache_reuse():
    """Test that running the same layered badge graph twice uses cache on second run."""
    # Register graphics ops
    registry = OpRegistry()
    registry.clear()
    register_core_ops(registry)

    # Define the graph (same as above)
    graph = {
        "background": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("72"), Decimal("72")),
                "color": (40, 40, 40, 255),
            },
            deps=[],
        ),
        "icon_stand_in": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("32"), Decimal("32")),
                "color": (0, 100, 200, 255),
            },
            deps=[],
        ),
        "badge": Node(
            op_name="gfx:create_solid",
            params={
                "size": (Decimal("12"), Decimal("12")),
                "color": (200, 0, 0, 255),
            },
            deps=[],
        ),
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": {
                    "background": absolute(0, 0),
                    "icon_stand_in": relative("background", "c,c"),
                    "badge": relative("icon_stand_in", "se,se", x=-2, y=2),
                },
            },
            deps=["background", "icon_stand_in", "badge"],
        ),
    }

    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    # First run: all ops execute
    results1 = executor.execute(graph)
    hash1 = results1["final"].get_stable_hash()

    # Second run: should use cache for all nodes
    results2 = executor.execute(graph)
    hash2 = results2["final"].get_stable_hash()

    # Verify results are identical
    assert hash1 == hash2
    assert results1["final"].width == results2["final"].width
    assert results1["final"].height == results2["final"].height
