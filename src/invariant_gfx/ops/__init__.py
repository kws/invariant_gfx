"""Graphics operations for Invariant GFX."""

from invariant_gfx.ops.blob_to_image import blob_to_image
from invariant_gfx.ops.brightness_contrast import brightness_contrast
from invariant_gfx.ops.colorize import colorize
from invariant_gfx.ops.composite import composite
from invariant_gfx.ops.create_solid import create_solid
from invariant_gfx.ops.crop import crop
from invariant_gfx.ops.crop_region import crop_region
from invariant_gfx.ops.crop_to_content import crop_to_content
from invariant_gfx.ops.dilate import dilate
from invariant_gfx.ops.erode import erode
from invariant_gfx.ops.extract_alpha import extract_alpha
from invariant_gfx.ops.flip import flip
from invariant_gfx.ops.gaussian_blur import gaussian_blur
from invariant_gfx.ops.gradient_opacity import gradient_opacity
from invariant_gfx.ops.grayscale import grayscale
from invariant_gfx.ops.invert_alpha import invert_alpha
from invariant_gfx.ops.layout import layout
from invariant_gfx.ops.mask_alpha import mask_alpha
from invariant_gfx.ops.opacity import opacity
from invariant_gfx.ops.packed_text import packed_text
from invariant_gfx.ops.pad import pad
from invariant_gfx.ops.render_svg import render_svg
from invariant_gfx.ops.render_text import render_text
from invariant_gfx.ops.resize import resize
from invariant_gfx.ops.resolve_color import resolve_color
from invariant_gfx.ops.resolve_resource import resolve_resource
from invariant_gfx.ops.rotate import rotate
from invariant_gfx.ops.threshold_alpha import threshold_alpha
from invariant_gfx.ops.thumbnail import thumbnail
from invariant_gfx.ops.tint import tint
from invariant_gfx.ops.transform import transform
from invariant_gfx.ops.translate import translate

OPS = {
    "blob_to_image": blob_to_image,
    "brightness_contrast": brightness_contrast,
    "colorize": colorize,
    "composite": composite,
    "create_solid": create_solid,
    "crop": crop,
    "crop_region": crop_region,
    "crop_to_content": crop_to_content,
    "dilate": dilate,
    "erode": erode,
    "extract_alpha": extract_alpha,
    "flip": flip,
    "gaussian_blur": gaussian_blur,
    "gradient_opacity": gradient_opacity,
    "grayscale": grayscale,
    "invert_alpha": invert_alpha,
    "layout": layout,
    "mask_alpha": mask_alpha,
    "opacity": opacity,
    "packed_text": packed_text,
    "pad": pad,
    "render_svg": render_svg,
    "render_text": render_text,
    "resolve_color": resolve_color,
    "resize": resize,
    "resolve_resource": resolve_resource,
    "rotate": rotate,
    "threshold_alpha": threshold_alpha,
    "thumbnail": thumbnail,
    "tint": tint,
    "transform": transform,
    "translate": translate,
}

__all__ = [
    "OPS",
    "blob_to_image",
    "brightness_contrast",
    "colorize",
    "composite",
    "create_solid",
    "crop",
    "crop_region",
    "crop_to_content",
    "dilate",
    "erode",
    "extract_alpha",
    "flip",
    "gaussian_blur",
    "gradient_opacity",
    "grayscale",
    "invert_alpha",
    "layout",
    "mask_alpha",
    "opacity",
    "packed_text",
    "pad",
    "render_svg",
    "render_text",
    "resolve_color",
    "resize",
    "resolve_resource",
    "rotate",
    "threshold_alpha",
    "thumbnail",
    "tint",
    "transform",
    "translate",
]


def register_core_ops(registry) -> None:
    """Register all core graphics operations with the OpRegistry.

    This function is idempotent: it will skip registration if an op is already
    registered. This allows multiple Pipeline instances to safely call this
    function when using a shared OpRegistry singleton.

    Args:
        registry: OpRegistry instance to register operations with.
    """
    for name, op in OPS.items():
        if not registry.has(name):
            registry.register(name, op)
