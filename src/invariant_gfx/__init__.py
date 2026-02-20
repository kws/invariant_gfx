"""invariant_gfx: A deterministic, DAG-based graphics engine built on Invariant."""

from invariant.registry import OpRegistry

__version__ = "0.1.0"

__all__ = ["register_core_ops", "__version__"]


def register_core_ops(registry: OpRegistry) -> None:
    """Register all core graphics operations in the OpRegistry.

    Args:
        registry: The OpRegistry instance to register operations in.
    """
    from invariant_gfx.ops import (
        blob_to_image,
        composite,
        create_solid,
        layout,
        render_svg,
        render_text,
        resize,
        resolve_resource,
    )

    ops_to_register = [
        ("gfx:create_solid", create_solid),
        ("gfx:resolve_resource", resolve_resource),
        ("gfx:render_svg", render_svg),
        ("gfx:render_text", render_text),
        ("gfx:resize", resize),
        ("gfx:composite", composite),
        ("gfx:layout", layout),
        ("gfx:blob_to_image", blob_to_image),
    ]

    for name, op in ops_to_register:
        if not registry.has(name):
            registry.register(name, op)
