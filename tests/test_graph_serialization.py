"""Tests for graph serialization with GFX graphs.

Verifies that GFX graphs (gfx:* ops, anchors, Decimal, tuples, ref, nested params)
round-trip correctly through Invariant's JSON wire format. Ensures nothing in
the GFX codebase produces params or structures that break serialization.
"""

from decimal import Decimal

from invariant import Node, SubGraphNode, cel, ref
from invariant.graph_serialization import dump_graph, load_graph
from invariant_gfx.anchors import relative


def _graphs_equal(g1: dict, g2: dict) -> bool:
    """Structural equality for graphs (Node/SubGraphNode comparison)."""
    if set(g1.keys()) != set(g2.keys()):
        return False
    for k in g1:
        v1, v2 = g1[k], g2[k]
        if type(v1) is not type(v2):
            return False
        if isinstance(v1, Node):
            if v1.op_name != v2.op_name or v1.deps != v2.deps or v1.cache != v2.cache:
                return False
            if v1.params != v2.params:
                return False
        else:
            if v1.deps != v2.deps or v1.output != v2.output:
                return False
            if v1.params != v2.params:
                return False
            if not _graphs_equal(v1.graph, v2.graph):
                return False
    return True


class TestGfxGraphRoundTrip:
    """Round-trip serialization of GFX graphs."""

    def test_create_solid_decimal_tuple(self):
        """gfx:create_solid with Decimal and tuple params round-trips."""
        graph = {
            "bg": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("72"), Decimal("72")),
                    "color": (40, 40, 40, 255),
                },
                deps=[],
            ),
        }
        g2 = load_graph(dump_graph(graph))
        assert _graphs_equal(graph, g2)

    def test_composite_with_anchors(self):
        """gfx:composite with layers, ref, absolute, relative round-trips."""
        graph = {
            "background": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("72"), Decimal("72")),
                    "color": (40, 40, 40, 255),
                },
                deps=[],
            ),
            "icon": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("32"), Decimal("32")),
                    "color": (0, 100, 200, 255),
                },
                deps=[],
            ),
            "final": Node(
                op_name="gfx:composite",
                params={
                    "layers": [
                        {"image": ref("background"), "id": "background"},
                        {
                            "image": ref("icon"),
                            "anchor": relative("background", "c@c"),
                            "id": "icon",
                        },
                    ],
                },
                deps=["background", "icon"],
            ),
        }
        g2 = load_graph(dump_graph(graph))
        assert _graphs_equal(graph, g2)

    def test_layout_with_ref_items(self):
        """gfx:layout with ref() in items list round-trips."""
        graph = {
            "block_a": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("20"), Decimal("30")),
                    "color": (200, 0, 0, 255),
                },
                deps=[],
            ),
            "block_b": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("20"), Decimal("20")),
                    "color": (0, 200, 0, 255),
                },
                deps=[],
            ),
            "row_layout": Node(
                op_name="gfx:layout",
                params={
                    "direction": "row",
                    "align": "c",
                    "gap": Decimal("5"),
                    "items": [ref("block_a"), ref("block_b")],
                },
                deps=["block_a", "block_b"],
            ),
        }
        g2 = load_graph(dump_graph(graph))
        assert _graphs_equal(graph, g2)

    def test_absolute_relative_anchor_params(self):
        """Anchor specs with Decimal and int params round-trip."""
        graph = {
            "bg": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("10"), Decimal("10")),
                    "color": (0, 0, 0, 255),
                },
                deps=[],
            ),
            "final": Node(
                op_name="gfx:composite",
                params={
                    "layers": [
                        {"image": ref("bg"), "id": "bg"},
                        {
                            "image": ref("bg"),
                            "anchor": relative("bg", "se@se", x=-2, y=2),
                            "id": "overlay",
                        },
                    ],
                },
                deps=["bg"],
            ),
        }
        g2 = load_graph(dump_graph(graph))
        assert _graphs_equal(graph, g2)

    def test_cel_expression_in_params(self):
        """Params with cel() expressions round-trip."""
        graph = {
            "x": Node(
                op_name="gfx:create_solid",
                params={"size": (1, 1), "color": (0, 0, 0, 255)},
                deps=[],
            ),
            "y": Node(
                op_name="gfx:resize",
                params={
                    "image": ref("x"),
                    "width": cel("decimal('50')"),
                    "height": cel("decimal('50')"),
                },
                deps=["x"],
            ),
        }
        g2 = load_graph(dump_graph(graph))
        assert _graphs_equal(graph, g2)

    def test_subgraph_with_gfx_ops(self):
        """SubGraphNode containing gfx ops round-trips."""
        inner = {
            "inner_bg": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("32"), Decimal("32")),
                    "color": (100, 100, 100, 255),
                },
                deps=[],
            ),
        }
        graph = {
            "outer": SubGraphNode(
                params={},
                deps=[],
                graph=inner,
                output="inner_bg",
            ),
        }
        g2 = load_graph(dump_graph(graph))
        assert _graphs_equal(graph, g2)


class TestGfxGraphExecuteAfterLoad:
    """Loaded graphs execute correctly (sanity check)."""

    def test_loaded_graph_executes(self):
        """Graph that round-trips can be executed."""
        from invariant import Executor
        from invariant.registry import OpRegistry
        from invariant.store.memory import MemoryStore
        from invariant_gfx import register_core_ops

        graph = {
            "bg": Node(
                op_name="gfx:create_solid",
                params={
                    "size": (Decimal("72"), Decimal("72")),
                    "color": (40, 40, 40, 255),
                },
                deps=[],
            ),
            "final": Node(
                op_name="gfx:composite",
                params={
                    "layers": [
                        {"image": ref("bg"), "id": "bg"},
                    ],
                },
                deps=["bg"],
            ),
        }
        serialized = dump_graph(graph)
        loaded = load_graph(serialized)

        registry = OpRegistry()
        registry.clear()
        register_core_ops(registry)
        store = MemoryStore()
        executor = Executor(registry=registry, store=store)

        results = executor.execute(loaded, ["final"])
        assert results["final"].width == 72
        assert results["final"].height == 72
