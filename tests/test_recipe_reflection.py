"""Tests for the reflection effect recipe (SubGraphNode)."""

from decimal import Decimal

from invariant import Executor, Node
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore
from invariant_gfx import register_core_ops
from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.recipes import reflection


def _make_executor():
    registry = OpRegistry()
    register_core_ops(registry)
    store = MemoryStore()
    return Executor(registry=registry, store=store)


def test_reflection_happy_path():
    """Execute a parent graph with reflection subgraph; output is ImageArtifact."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (20, 20), "color": (255, 255, 255, 255)},
            deps=[],
        ),
        "refl": reflection("source"),
    }
    results = executor.execute(graph, ["source", "refl"])
    assert "source" in results
    assert "refl" in results
    assert isinstance(results["source"], ImageArtifact)
    assert isinstance(results["refl"], ImageArtifact)
    # Reflection is same size as source when squash=1, gap=0
    assert results["refl"].width == results["source"].width
    assert results["refl"].height == results["source"].height


def test_reflection_with_squash():
    """squash < 1 compresses reflection vertically."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (30, 40), "color": (200, 200, 200, 255)},
            deps=[],
        ),
        "refl": reflection("source", squash=Decimal("0.5")),
    }
    results = executor.execute(graph, ["refl"])
    assert results["refl"].width == 30
    assert results["refl"].height == 20  # 40 * 0.5


def test_reflection_with_skew():
    """skew != 0 applies shear; crop_to_content trims transparent regions."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (20, 20), "color": (100, 100, 100, 255)},
            deps=[],
        ),
        "refl": reflection("source", skew=Decimal("0.05")),
    }
    results = executor.execute(graph, ["refl"])
    assert isinstance(results["refl"], ImageArtifact)
    # crop_to_content keeps only alpha > 0; gradient fades to 0 at end_pos=0.5
    assert results["refl"].width >= 20
    assert results["refl"].height >= 1  # at least the opaque top portion


def test_reflection_with_gap():
    """gap > 0 translates reflection down; output height increases."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (20, 20), "color": (255, 255, 255, 255)},
            deps=[],
        ),
        "refl": reflection("source", gap=10),
    }
    results = executor.execute(graph, ["refl"])
    assert results["refl"].width == 20
    assert results["refl"].height == 30  # 20 + 10


def test_reflection_squash_and_skew():
    """squash and skew together produce perspective-like reflection."""
    executor = _make_executor()
    graph = {
        "source": Node(
            op_name="gfx:create_solid",
            params={"size": (24, 32), "color": (180, 180, 180, 255)},
            deps=[],
        ),
        "refl": reflection(
            "source",
            squash=Decimal("0.5"),
            skew=Decimal("0.03"),
        ),
    }
    results = executor.execute(graph, ["refl"])
    assert isinstance(results["refl"], ImageArtifact)
    # Squashed: height = 32 * 0.5 = 16; crop_to_content trims bottom (alpha=0)
    assert results["refl"].width >= 24
    assert results["refl"].height == 8  # top half of 16 (gradient end_pos=0.5)
