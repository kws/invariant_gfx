"""Graphics operations for Invariant GFX."""

from invariant.traits import OpTrait, op_traits

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

LOW_COST_TRAIT = "low-cost"

_IMAGE_OP_TRAITS = (
    OpTrait.BLOCKING,
    OpTrait.CPU_BOUND,
    OpTrait.THREAD_SAFE,
    OpTrait.PROCESS_SAFE,
)
_RESOURCE_OP_TRAITS = (
    OpTrait.BLOCKING,
    OpTrait.IO_BOUND,
    OpTrait.THREAD_SAFE,
    OpTrait.PROCESS_SAFE,
)
_TEXT_OP_TRAITS = (
    OpTrait.BLOCKING,
    OpTrait.CPU_BOUND,
    OpTrait.IO_BOUND,
    OpTrait.THREAD_SAFE,
    OpTrait.PROCESS_SAFE,
)
_LOW_COST_OP_TRAITS = (
    LOW_COST_TRAIT,
    OpTrait.THREAD_SAFE,
    OpTrait.PROCESS_SAFE,
)

_RAW_OPS = {
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

OP_TRAITS = {
    "blob_to_image": _IMAGE_OP_TRAITS,
    "brightness_contrast": _IMAGE_OP_TRAITS,
    "colorize": _IMAGE_OP_TRAITS,
    "composite": _IMAGE_OP_TRAITS,
    "create_solid": _IMAGE_OP_TRAITS,
    "crop": _IMAGE_OP_TRAITS,
    "crop_region": _IMAGE_OP_TRAITS,
    "crop_to_content": _IMAGE_OP_TRAITS,
    "dilate": _IMAGE_OP_TRAITS,
    "erode": _IMAGE_OP_TRAITS,
    "extract_alpha": _IMAGE_OP_TRAITS,
    "flip": _IMAGE_OP_TRAITS,
    "gaussian_blur": _IMAGE_OP_TRAITS,
    "gradient_opacity": _IMAGE_OP_TRAITS,
    "grayscale": _IMAGE_OP_TRAITS,
    "invert_alpha": _IMAGE_OP_TRAITS,
    "layout": _IMAGE_OP_TRAITS,
    "mask_alpha": _IMAGE_OP_TRAITS,
    "opacity": _IMAGE_OP_TRAITS,
    "packed_text": _TEXT_OP_TRAITS,
    "pad": _IMAGE_OP_TRAITS,
    "render_svg": _IMAGE_OP_TRAITS,
    "render_text": _TEXT_OP_TRAITS,
    "resize": _IMAGE_OP_TRAITS,
    "resolve_color": _LOW_COST_OP_TRAITS,
    "resolve_resource": _RESOURCE_OP_TRAITS,
    "rotate": _IMAGE_OP_TRAITS,
    "threshold_alpha": _IMAGE_OP_TRAITS,
    "thumbnail": _IMAGE_OP_TRAITS,
    "tint": _IMAGE_OP_TRAITS,
    "transform": _IMAGE_OP_TRAITS,
    "translate": _IMAGE_OP_TRAITS,
}

if set(OP_TRAITS) != set(_RAW_OPS):
    missing = sorted(set(_RAW_OPS) - set(OP_TRAITS))
    extra = sorted(set(OP_TRAITS) - set(_RAW_OPS))
    raise RuntimeError(
        "gfx op trait metadata must cover OPS exactly: "
        f"missing={missing}, extra={extra}"
    )

OPS = {
    name: op_traits(*OP_TRAITS[name])(op)
    for name, op in _RAW_OPS.items()
}

__all__ = [
    "LOW_COST_TRAIT",
    "OPS",
    "OP_TRAITS",
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
