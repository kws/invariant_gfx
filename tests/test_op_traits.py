"""Tests for gfx operation scheduler traits."""

import asyncio

from invariant.registry import OpRegistry
from invariant.scheduler import InvocationRequest, ProcessPoolScheduler
from invariant.traits import OpTrait
from invariant_gfx import register_core_ops
from invariant_gfx.artifacts import ImageArtifact
from invariant_gfx.ops import LOW_COST_TRAIT, OP_TRAITS, OPS

_IMAGE_OPS = {
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
    "pad",
    "render_svg",
    "resize",
    "rotate",
    "threshold_alpha",
    "thumbnail",
    "tint",
    "transform",
    "translate",
}

_IMAGE_TRAITS = frozenset(
    {
        OpTrait.BLOCKING.value,
        OpTrait.CPU_BOUND.value,
        OpTrait.THREAD_SAFE.value,
        OpTrait.PROCESS_SAFE.value,
    }
)
_RESOURCE_TRAITS = frozenset(
    {
        OpTrait.BLOCKING.value,
        OpTrait.IO_BOUND.value,
        OpTrait.THREAD_SAFE.value,
        OpTrait.PROCESS_SAFE.value,
    }
)
_TEXT_TRAITS = frozenset(
    {
        OpTrait.BLOCKING.value,
        OpTrait.CPU_BOUND.value,
        OpTrait.IO_BOUND.value,
        OpTrait.THREAD_SAFE.value,
        OpTrait.PROCESS_SAFE.value,
    }
)
_LOW_COST_TRAITS = frozenset(
    {
        LOW_COST_TRAIT,
        OpTrait.THREAD_SAFE.value,
        OpTrait.PROCESS_SAFE.value,
    }
)


def _fresh_registry() -> OpRegistry:
    registry = OpRegistry()
    registry.clear()
    return registry


def test_register_core_ops_exposes_expected_traits_and_refs():
    registry = _fresh_registry()
    register_core_ops(registry)

    assert set(OP_TRAITS) == set(OPS)

    for op_name in _IMAGE_OPS:
        full_name = f"gfx:{op_name}"
        assert registry.traits(full_name) == _IMAGE_TRAITS
        assert registry.implementation_ref(full_name) == (
            f"invariant_gfx.ops.{op_name}:{op_name}"
        )

    assert registry.traits("gfx:resolve_resource") == _RESOURCE_TRAITS
    assert registry.traits("gfx:render_text") == _TEXT_TRAITS
    assert registry.traits("gfx:packed_text") == _TEXT_TRAITS
    assert registry.traits("gfx:resolve_color") == _LOW_COST_TRAITS


def test_auto_discovery_preserves_gfx_traits():
    registry = _fresh_registry()
    registry.auto_discover()

    assert registry.traits("gfx:create_solid") == _IMAGE_TRAITS
    assert registry.traits("gfx:resolve_resource") == _RESOURCE_TRAITS
    assert registry.traits("gfx:render_text") == _TEXT_TRAITS
    assert registry.traits("gfx:resolve_color") == _LOW_COST_TRAITS
    assert registry.implementation_ref("gfx:create_solid") == (
        "invariant_gfx.ops.create_solid:create_solid"
    )


def test_process_scheduler_executes_representative_image_op():
    registry = _fresh_registry()
    register_core_ops(registry)
    binding = registry.get_binding("gfx:create_solid")
    request = InvocationRequest(
        op_name=binding.name,
        op=binding.op,
        manifest={"size": (8, 6), "color": (10, 20, 30, 255)},
        traits=binding.traits,
        implementation_ref=binding.implementation_ref,
    )

    async def run() -> ImageArtifact:
        scheduler = ProcessPoolScheduler(max_workers=1)
        try:
            return await scheduler.invoke(request)
        finally:
            await scheduler.aclose()

    result = asyncio.run(run())

    assert isinstance(result, ImageArtifact)
    assert result.width == 8
    assert result.height == 6


def test_process_scheduler_executes_low_cost_op():
    registry = _fresh_registry()
    register_core_ops(registry)
    binding = registry.get_binding("gfx:resolve_color")
    request = InvocationRequest(
        op_name=binding.name,
        op=binding.op,
        manifest={"color": "#ff00cc"},
        traits=binding.traits,
        implementation_ref=binding.implementation_ref,
    )

    async def run() -> tuple[int, int, int, int]:
        scheduler = ProcessPoolScheduler(max_workers=1)
        try:
            return await scheduler.invoke(request)
        finally:
            await scheduler.aclose()

    assert asyncio.run(run()) == (255, 0, 204, 255)
