"""Invariant GFX: A deterministic, DAG-based graphics engine built on Invariant."""

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
        colorize,
        composite,
        crop,
        create_solid,
        dilate,
        erode,
        extract_alpha,
        gaussian_blur,
        invert_alpha,
        layout,
        mask_alpha,
        opacity,
        pad,
        threshold_alpha,
        translate,
        render_svg,
        render_text,
        resize,
        resolve_resource,
    )

    ops_to_register = [
        ("gfx:create_solid", create_solid),
        ("gfx:dilate", dilate),
        ("gfx:erode", erode),
        ("gfx:gaussian_blur", gaussian_blur),
        ("gfx:resolve_resource", resolve_resource),
        ("gfx:render_svg", render_svg),
        ("gfx:render_text", render_text),
        ("gfx:resize", resize),
        ("gfx:colorize", colorize),
        ("gfx:composite", composite),
        ("gfx:crop", crop),
        ("gfx:layout", layout),
        ("gfx:opacity", opacity),
        ("gfx:blob_to_image", blob_to_image),
        ("gfx:extract_alpha", extract_alpha),
        ("gfx:invert_alpha", invert_alpha),
        ("gfx:mask_alpha", mask_alpha),
        ("gfx:pad", pad),
        ("gfx:threshold_alpha", threshold_alpha),
        ("gfx:translate", translate),
    ]

    for name, op in ops_to_register:
        if not registry.has(name):
            registry.register(name, op)
