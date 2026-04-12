"""Effect recipes: pre-bundled subgraphs (drop shadow, stroke, glow, etc.)."""

from invariant_gfx.recipes.drop_shadow import drop_shadow
from invariant_gfx.recipes.inner_glow import inner_glow
from invariant_gfx.recipes.inner_shadow import inner_shadow
from invariant_gfx.recipes.outer_glow import outer_glow
from invariant_gfx.recipes.outer_stroke import outer_stroke
from invariant_gfx.recipes.reflection import reflection

__all__ = [
    "drop_shadow",
    "inner_glow",
    "inner_shadow",
    "outer_glow",
    "outer_stroke",
    "reflection",
]
