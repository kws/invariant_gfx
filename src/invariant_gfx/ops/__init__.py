"""Graphics operations for Invariant GFX."""

from invariant_gfx.ops.blob_to_image import blob_to_image
from invariant_gfx.ops.colorize import colorize
from invariant_gfx.ops.composite import composite
from invariant_gfx.ops.crop import crop
from invariant_gfx.ops.create_solid import create_solid
from invariant_gfx.ops.dilate import dilate
from invariant_gfx.ops.erode import erode
from invariant_gfx.ops.extract_alpha import extract_alpha
from invariant_gfx.ops.gaussian_blur import gaussian_blur
from invariant_gfx.ops.invert_alpha import invert_alpha
from invariant_gfx.ops.layout import layout
from invariant_gfx.ops.mask_alpha import mask_alpha
from invariant_gfx.ops.opacity import opacity
from invariant_gfx.ops.pad import pad
from invariant_gfx.ops.threshold_alpha import threshold_alpha
from invariant_gfx.ops.translate import translate
from invariant_gfx.ops.render_svg import render_svg
from invariant_gfx.ops.render_text import render_text
from invariant_gfx.ops.resolve_resource import resolve_resource
from invariant_gfx.ops.resize import resize

__all__ = [
    "blob_to_image",
    "colorize",
    "composite",
    "crop",
    "create_solid",
    "dilate",
    "erode",
    "extract_alpha",
    "gaussian_blur",
    "invert_alpha",
    "layout",
    "mask_alpha",
    "opacity",
    "pad",
    "threshold_alpha",
    "translate",
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
        ("dilate", dilate),
        ("erode", erode),
        ("gaussian_blur", gaussian_blur),
        ("resolve_resource", resolve_resource),
        ("render_svg", render_svg),
        ("render_text", render_text),
        ("resize", resize),
        ("composite", composite),
        ("crop", crop),
        ("colorize", colorize),
        ("layout", layout),
        ("opacity", opacity),
        ("blob_to_image", blob_to_image),
        ("extract_alpha", extract_alpha),
        ("invert_alpha", invert_alpha),
        ("mask_alpha", mask_alpha),
        ("pad", pad),
        ("threshold_alpha", threshold_alpha),
        ("translate", translate),
    ]

    for name, op in ops_to_register:
        if not registry.has(name):
            registry.register(name, op)
