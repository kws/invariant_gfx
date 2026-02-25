"""Graphics operations for Invariant GFX."""

from invariant_gfx.ops.blob_to_image import blob_to_image
from invariant_gfx.ops.brightness_contrast import brightness_contrast
from invariant_gfx.ops.colorize import colorize
from invariant_gfx.ops.composite import composite
from invariant_gfx.ops.crop import crop
from invariant_gfx.ops.crop_region import crop_region
from invariant_gfx.ops.crop_to_content import crop_to_content
from invariant_gfx.ops.create_solid import create_solid
from invariant_gfx.ops.dilate import dilate
from invariant_gfx.ops.erode import erode
from invariant_gfx.ops.extract_alpha import extract_alpha
from invariant_gfx.ops.flip import flip
from invariant_gfx.ops.gaussian_blur import gaussian_blur
from invariant_gfx.ops.grayscale import grayscale
from invariant_gfx.ops.invert_alpha import invert_alpha
from invariant_gfx.ops.layout import layout
from invariant_gfx.ops.mask_alpha import mask_alpha
from invariant_gfx.ops.opacity import opacity
from invariant_gfx.ops.pad import pad
from invariant_gfx.ops.threshold_alpha import threshold_alpha
from invariant_gfx.ops.tint import tint
from invariant_gfx.ops.translate import translate
from invariant_gfx.ops.render_svg import render_svg
from invariant_gfx.ops.render_text import render_text
from invariant_gfx.ops.resolve_resource import resolve_resource
from invariant_gfx.ops.resize import resize
from invariant_gfx.ops.rotate import rotate
from invariant_gfx.ops.thumbnail import thumbnail

__all__ = [
    "blob_to_image",
    "brightness_contrast",
    "colorize",
    "composite",
    "crop",
    "crop_region",
    "crop_to_content",
    "create_solid",
    "dilate",
    "erode",
    "extract_alpha",
    "flip",
    "gaussian_blur",
    "grayscale",
    "invert_alpha",
    "layout",
    "mask_alpha",
    "opacity",
    "pad",
    "threshold_alpha",
    "tint",
    "translate",
    "render_svg",
    "render_text",
    "resize",
    "resolve_resource",
    "rotate",
    "thumbnail",
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
        ("flip", flip),
        ("gaussian_blur", gaussian_blur),
        ("resolve_resource", resolve_resource),
        ("render_svg", render_svg),
        ("render_text", render_text),
        ("resize", resize),
        ("rotate", rotate),
        ("thumbnail", thumbnail),
        ("brightness_contrast", brightness_contrast),
        ("crop_region", crop_region),
        ("crop_to_content", crop_to_content),
        ("grayscale", grayscale),
        ("tint", tint),
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
