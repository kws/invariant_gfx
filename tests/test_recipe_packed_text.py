"""Tests for the packed_text op."""

from invariant import Executor, Node
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.artifacts import ImageArtifact


def _make_executor():
    registry = OpRegistry()
    register_core_ops(registry)
    store = MemoryStore()
    return Executor(registry=registry, store=store)


def test_packed_text_fits_canvas():
    """Op should render and fit a fixed-size output."""
    executor = _make_executor()
    graph = {
        "label": Node(
            op_name="gfx:packed_text",
            params={
                "text": "Momentary lapse of Reason",
                "size": (196, 196),
                "font": "Geneva",
                "min_font_size": 12,
                "max_font_size": 42,
                "align_horizontal": "center",
                "align_vertical": "center",
            },
            deps=[],
        )
    }

    results = executor.execute(graph)
    assert isinstance(results["label"], ImageArtifact)
    assert results["label"].width == 196
    assert results["label"].height == 196


def test_packed_text_handles_long_single_token():
    """A single oversized token should be truncated with ellipsis and still render."""
    executor = _make_executor()
    graph = {
        "label": Node(
            op_name="gfx:packed_text",
            params={
                "text": "Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch",
                "size": (196, 196),
                "font": "Geneva",
                "min_font_size": 10,
                "max_font_size": 40,
                "align_horizontal": "left",
                "align_vertical": "top",
            },
            deps=[],
        )
    }

    results = executor.execute(graph)
    assert results["label"].width == 196
    assert results["label"].height == 196


def test_packed_text_handles_extreme_phrase_with_drop():
    """Very long phrases should still render by reducing size and dropping trailing words."""
    executor = _make_executor()
    graph = {
        "label": Node(
            op_name="gfx:packed_text",
            params={
                "text": (
                    "Music to Listen to~Dance to~Blaze to~Pray to~Feed to~Sleep to~Talk to~"
                    "Grind to~Trip to~Breathe to~Help to~Hurt to~Scroll to~Roll to~Love to~"
                    "Hate to~Learn Too~Plot to~Play to~Be to~Feel to~Breed to~Sweat to~"
                    "Dream to~Hide to~Live to~Die to~Go To"
                ),
                "size": (196, 196),
                "font": "Geneva",
                "min_font_size": 8,
                "max_font_size": 32,
                "align_horizontal": "right",
                "align_vertical": "bottom",
            },
            deps=[],
        )
    }

    results = executor.execute(graph)
    assert results["label"].width == 196
    assert results["label"].height == 196
