"""Integration tests for invariant_gfx pipeline."""

from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import relative
from invariant_gfx.artifacts import ImageArtifact


def test_thermometer_button_template():
    """Test rendering a thermometer button template with context."""
    registry = OpRegistry()
    register_core_ops(registry)
    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    # Define template graph
    template = {
        # Resolve icon resource (depends on context "icon")
        "icon_blob": Node(
            op_name="gfx:resolve_resource",
            params={"name": "${icon}"},
            deps=["icon"],
        ),
        # Render icon SVG to raster
        "icon_image": Node(
            op_name="gfx:render_svg",
            params={
                "svg_content": ref("icon_blob"),
                "width": 50,
                "height": 50,
            },
            deps=["icon_blob"],
        ),
        # Render temperature text (depends on context "temperature")
        "text": Node(
            op_name="gfx:render_text",
            params={
                "text": "${temperature}",
                "font": "Inter",
                "size": 12,
                "color": (255, 255, 255, 255),  # White RGBA
            },
            deps=["temperature"],
        ),
        # Create background
        "background": Node(
            op_name="gfx:create_solid",
            params={
                "size": (72, 72),  # Fixed for this test
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
                "gap": 5,
                "items": [ref("icon_image"), ref("text")],
            },
            deps=["icon_image", "text"],
        ),
        # Composite onto background
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {
                        "image": ref("background"),
                        "id": "bg",
                    },
                    {
                        "image": ref("content"),
                        "anchor": relative("bg", "c@c"),
                        "id": "content_layer",
                    },
                ],
            },
            deps=["background", "content"],
        ),
    }

    # Render with context
    results1 = executor.execute(
        graph=template,
        context={
            "icon": "lucide:thermometer",
            "temperature": "22.5°C",
        },
    )
    result1: ImageArtifact = results1["final"]

    # Verify result
    assert isinstance(result1, ImageArtifact)
    assert result1.width == 72
    assert result1.height == 72

    # Render again with different context (should use cache for shared artifacts)
    results2 = executor.execute(
        graph=template,
        context={
            "icon": "lucide:thermometer",  # Same icon (should be cached)
            "temperature": "18.0°C",  # Different temperature
        },
    )
    result2: ImageArtifact = results2["final"]

    # Verify result
    assert isinstance(result2, ImageArtifact)
    assert result2.width == 72
    assert result2.height == 72

    # Results should be different (different temperature text)
    assert result1.get_stable_hash() != result2.get_stable_hash()


def test_simple_square_canvas():
    """Test rendering a simple square canvas with icon and text."""
    registry = OpRegistry()
    register_core_ops(registry)
    store = MemoryStore()
    executor = Executor(registry=registry, store=store)

    template = {
        "icon_blob": Node(
            op_name="gfx:resolve_resource",
            params={"name": "${icon}"},
            deps=["icon"],
        ),
        "icon_image": Node(
            op_name="gfx:render_svg",
            params={
                "svg_content": ref("icon_blob"),
                "width": 40,
                "height": 40,
            },
            deps=["icon_blob"],
        ),
        "text": Node(
            op_name="gfx:render_text",
            params={
                "text": "${label}",
                "font": "Inter",
                "size": 14,
                "color": (255, 255, 255, 255),
            },
            deps=["label"],
        ),
        "background": Node(
            op_name="gfx:create_solid",
            params={"size": (64, 64), "color": (0, 128, 255, 255)},
            deps=[],
        ),
        "content": Node(
            op_name="gfx:layout",
            params={
                "direction": "column",
                "align": "c",
                "gap": 4,
                "items": [ref("icon_image"), ref("text")],
            },
            deps=["icon_image", "text"],
        ),
        "final": Node(
            op_name="gfx:composite",
            params={
                "layers": [
                    {
                        "image": ref("background"),
                        "id": "bg",
                    },
                    {
                        "image": ref("content"),
                        "anchor": relative("bg", "c@c"),
                    },
                ],
            },
            deps=["background", "content"],
        ),
    }

    results = executor.execute(
        graph=template,
        context={
            "icon": "lucide:lightbulb",
            "label": "ON",
        },
    )
    result = results["final"]

    assert isinstance(result, ImageArtifact)
    assert result.width == 64
    assert result.height == 64
