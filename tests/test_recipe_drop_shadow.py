"""Tests for the drop_shadow effect recipe (SubGraphNode)."""

from decimal import Decimal

from invariant import Executor, Node
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore
from invariant_gfx import register_core_ops
from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.recipes import drop_shadow


def _make_executor():
    registry = OpRegistry()
    register_core_ops(registry)
    store = MemoryStore()
    return Executor(registry=registry, store=store)


def test_drop_shadow_happy_path():
    """Execute a parent graph with a drop_shadow subgraph."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (20, 20), "color": (255, 255, 255, 255)},
            deps=[],
        ),
        "shadow": drop_shadow("source", dx=2, dy=2, sigma=Decimal("3")),
    }
    results = executor.execute(graph, ["source", "shadow"])
    assert "source" in results
    assert "shadow" in results
    assert isinstance(results["source"], ImageArtifact)
    assert isinstance(results["shadow"], ImageArtifact)
    # Shadow is blurred and translated, so output can be larger than source
    source_img = results["source"].image
    shadow_img = results["shadow"].image
    assert shadow_img.size[0] >= source_img.size[0]
    assert shadow_img.size[1] >= source_img.size[1]


def test_drop_shadow_context_wiring():
    """Subgraph output differs from source after blur and translate."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (10, 10), "color": (200, 200, 200, 255)},
            deps=[],
        ),
        "shadow": drop_shadow("source", dx=3, dy=3, sigma=Decimal("2")),
    }
    results = executor.execute(graph, ["source", "shadow"])
    source_artifact = results["source"]
    shadow_artifact = results["shadow"]
    assert source_artifact is not shadow_artifact
    # Translate expands canvas, so shadow width/height should be strictly larger
    assert shadow_artifact.width >= source_artifact.width + 3
    assert shadow_artifact.height >= source_artifact.height + 3


def test_drop_shadow_with_radius_includes_dilate():
    """radius > 0 adds dilate node; execution succeeds."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (16, 16), "color": (255, 255, 255, 255)},
            deps=[],
        ),
        "shadow": drop_shadow("source", dx=1, dy=1, radius=2, sigma=Decimal("1")),
    }
    results = executor.execute(graph, ["shadow"])
    assert isinstance(results["shadow"], ImageArtifact)


def test_drop_shadow_zero_offset_omits_translate():
    """dx=0, dy=0 omits translate node; output is 'colored' node; execution succeeds."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (12, 12), "color": (255, 255, 255, 255)},
            deps=[],
        ),
        "shadow": drop_shadow("source", dx=0, dy=0, sigma=Decimal("1")),
    }
    results = executor.execute(graph, ["shadow"])
    assert isinstance(results["shadow"], ImageArtifact)
    # No translate: shadow size should be same or close to source.
    assert results["shadow"].width >= 12
    assert results["shadow"].height >= 12
