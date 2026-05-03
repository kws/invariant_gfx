"""Invariant GFX: A deterministic, DAG-based graphics engine built on Invariant."""

from importlib.metadata import version

from invariant.registry import OpRegistry

from invariant_gfx.recipes import drop_shadow

__version__ = version("invariant-gfx")

__all__ = ["drop_shadow", "register_core_ops", "__version__"]


def register_core_ops(registry: OpRegistry) -> None:
    """Register all core graphics operations in the OpRegistry.

    Args:
        registry: The OpRegistry instance to register operations in.
    """
    from invariant_gfx.ops import OPS

    for name, op in OPS.items():
        name = f"gfx:{name}"
        if not registry.has(name):
            registry.register(name, op)
