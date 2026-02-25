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
    from invariant_gfx.ops import (
        blob_to_image,
        brightness_contrast,
        colorize,
        composite,
        crop,
        crop_region,
        crop_to_content,
        create_solid,
        dilate,
        erode,
        extract_alpha,
        flip,
        gaussian_blur,
        gradient_opacity,
        grayscale,
        invert_alpha,
        layout,
        mask_alpha,
        opacity,
        pad,
        render_svg,
        render_text,
        resize,
        resolve_resource,
        rotate,
        threshold_alpha,
        thumbnail,
        tint,
        transform,
        translate,
    )

    ops_to_register = [
        ("gfx:create_solid", create_solid),
        ("gfx:dilate", dilate),
        ("gfx:erode", erode),
        ("gfx:flip", flip),
        ("gfx:gaussian_blur", gaussian_blur),
        ("gfx:gradient_opacity", gradient_opacity),
        ("gfx:resolve_resource", resolve_resource),
        ("gfx:render_svg", render_svg),
        ("gfx:render_text", render_text),
        ("gfx:resize", resize),
        ("gfx:rotate", rotate),
        ("gfx:thumbnail", thumbnail),
        ("gfx:transform", transform),
        ("gfx:brightness_contrast", brightness_contrast),
        ("gfx:crop_region", crop_region),
        ("gfx:crop_to_content", crop_to_content),
        ("gfx:grayscale", grayscale),
        ("gfx:tint", tint),
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
