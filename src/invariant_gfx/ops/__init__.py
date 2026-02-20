"""Graphics operations for invariant_gfx."""

from invariant_gfx.ops.blob_to_image import blob_to_image
from invariant_gfx.ops.composite import composite
from invariant_gfx.ops.create_solid import create_solid
from invariant_gfx.ops.layout import layout
from invariant_gfx.ops.render_svg import render_svg
from invariant_gfx.ops.render_text import render_text
from invariant_gfx.ops.resolve_resource import resolve_resource
from invariant_gfx.ops.resize import resize

__all__ = [
    "blob_to_image",
    "composite",
    "create_solid",
    "layout",
    "render_svg",
    "render_text",
    "resize",
    "resolve_resource",
]


def register_core_ops(registry) -> None:
    """Register all core graphics operations with the OpRegistry.

    This function is idempotent: it will skip registration if an op is already
    registered. This allows multiple Pipeline instances to safely call this
    function when using a shared OpRegistry singleton.

    Args:
        registry: OpRegistry instance to register operations with.
    """
    ops_to_register = [
        ("create_solid", create_solid),
        ("resolve_resource", resolve_resource),
        ("render_svg", render_svg),
        ("render_text", render_text),
        ("resize", resize),
        ("composite", composite),
        ("layout", layout),
        ("blob_to_image", blob_to_image),
    ]

    for name, op in ops_to_register:
        if not registry.has(name):
            registry.register(name, op)
