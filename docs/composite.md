# **gfx:composite Operation Specification**

Fixed-size composition engine. Stacks multiple layers onto a fixed-size canvas where each layer anchors to a previously-placed layer using a parent reference.

## **Inputs**

* `layers`: `list[dict]` — ordered by z-order (first drawn first, i.e. bottommost)
  * Each dict has these fields:
    * `image`: `ImageArtifact` — the layer content. In node params, this is typically provided via `ref("dep_name")`, which resolves to the upstream `ImageArtifact` during **Phase 1 (Context Resolution)**. The op receives the resolved artifact, not the `ref()` marker.
    * `anchor`: `dict` — positioning spec returned by `absolute()` or `relative()` builder functions. **Required for all layers except the first.** **Forbidden on the first layer** — the first layer IS the canvas.
    * `id`: `str` (optional) — a unique identifier for this layer. Required if any subsequent layer's `relative()` anchor references this layer. Not required otherwise.
  * The first layer defines the canvas. It must contain only `image` (and optionally `id`). The `anchor` field is **not allowed** — the op raises an error if present. The first layer is always placed at the origin (0, 0) and its image dimensions become the output dimensions. Typical pattern: use `gfx:create_solid` upstream to produce a solid-color canvas and place it as the first layer.
  * Subsequent layers are composited onto the canvas in list order. Each layer's image is immutable — the op works on an internal mutable copy of the canvas, never modifying upstream artifacts.

## **Output**

Returns a **new** `ImageArtifact` (RGBA mode) whose dimensions match the first layer's image dimensions. The composited result is produced by layering all images onto a canvas in list order. Upstream artifacts are never modified — the op works on an internal mutable copy of the canvas, producing a new immutable artifact as output.

## **Anchor Functions**

Anchor specifications are created using builder functions that return plain dicts (for compatibility with Invariant's expression resolver):

### **`absolute(x, y)`**

Place at absolute pixel coordinates on the canvas:

```python
absolute(x=0, y=0)  # Top-left corner
absolute(x=10, y=20)  # Specific pixel position
```

**Parameters:**
* `x`: `int | Decimal | str` (pixel offset from left edge). Accepts `str` for deferred `${...}` CEL expressions.
* `y`: `int | Decimal | str` (pixel offset from top edge). Accepts `str` for deferred `${...}` CEL expressions.

### **`relative(parent, align, x=0, y=0)`**

Position relative to a previously-placed layer:

```python
relative("background", "c@c")  # Center on background layer
relative("folder", "c@es", x=5, y=-5)  # Centered on folder's top-right corner, with offset
```

**Parameters:**
* `parent`: `str` (layer ID — the `id` field of a previously-listed layer). Must reference a layer that appears earlier in the list (lower index).
* `align`: `str` (alignment string, see Alignment String Format below).
* `x`: `int | Decimal | str` (optional horizontal offset in pixels, default 0). Accepts `str` for deferred `${...}` CEL expressions.
* `y`: `int | Decimal | str` (optional vertical offset in pixels, default 0). Accepts `str` for deferred `${...}` CEL expressions.

## **Alignment String Format**

Format: `"self@parent"` — reads as "place my [self point] **at** parent's [parent point]".

Each side uses 1 or 2 characters from `s` (start), `c` (center), `e` (end):
* **1 character** → shorthand, applies to both axes: `c` means `cc`, `s` means `ss`, `e` means `ee`
* **2 characters** → first is x-axis, second is y-axis

**Anchor Point Grid** (first char = x-axis, second char = y-axis):

```
         x=s       x=c       x=e
        (left)   (center)  (right)
       ┌─────────────────────────┐
y=s    │  ss        cs       es  │  (top)
       │                         │
y=c    │  sc        cc       ec  │  (middle)
       │                         │
y=e    │  se        ce       ee  │  (bottom)
       └─────────────────────────┘
```

**Inside Placement Examples** (self and parent use the same anchor point):
* `"c@c"` = center at center (centered) — shorthand for `"cc@cc"`
* `"s@s"` = top-left at top-left (flush) — shorthand for `"ss@ss"`
* `"e@e"` = bottom-right at bottom-right (flush) — shorthand for `"ee@ee"`

**Outside Placement Examples** (self and parent use different anchor points):
* `"c@es"` = my center at parent's top-right (badge centered on corner) — expands to `"cc@es"`
* `"se@es"` = my bottom-left at parent's top-right (badge extending outward from corner)
* `"ss@es"` = my top-left at parent's top-right (adjacent to the right)
* `"ss@se"` = my top-left at parent's bottom-left (stacked below)

## **Z-Ordering**

**List position IS z-order.** With a list-based design, z-order is explicit and unambiguous — layers are drawn in list order (index 0 = bottommost, highest index = topmost).

**Rules:**
* Layers are drawn in list order (index 0 = bottommost)
* `relative()` can only reference layers with a *lower* index (already placed)
* The first layer defines the canvas size. It must not have an `anchor` field. All subsequent layers must have an `anchor` field.

## **Additional Layer Properties**

Each layer dict in the `layers` list can optionally include these fields alongside the required fields (`image`, and `anchor` for non-first layers, `id` if needed):
* `mode`: `str` (blend mode: `"normal"`, `"multiply"`, `"screen"`, `"overlay"`, `"darken"`, `"lighten"`, `"add"`, default `"normal"`).
* `opacity`: `Decimal` (0.0 to 1.0, default 1.0).

**Example with opacity:**
```python
{
    "image": ref("overlay"),
    "anchor": relative("background", "c@c", y=5),  # Center, shifted 5px down
    "id": "overlay",
    "opacity": Decimal("0.8"),  # 80% opacity
}
```

## **Examples**

### Simple Two-Layer Composition

Background + centered content:

```python
"final": Node(
    op_name="gfx:composite",
    params={
        "layers": [
            {
                "image": ref("background"),
                "id": "background",
            },
            {
                "image": ref("content"),
                "anchor": relative("background", "c@c"),
                "id": "content",
            },
        ],
    },
    deps=["background", "content"],
)
```

### Three-Layer: Icon with Badge

Folder icon with badge on top-right corner:

```python
"final": Node(
    op_name="gfx:composite",
    params={
        "layers": [
            {
                "image": ref("background"),
                "id": "background",
            },
            {
                "image": ref("folder"),
                "anchor": relative("background", "c@c"),  # Folder centered on background
                "id": "folder",
            },
            {
                "image": ref("badge"),
                "anchor": relative("folder", "c@es"),  # Badge centered on folder's top-right
                "id": "badge",
            },
        ],
    },
    deps=["background", "folder", "badge"],
)
```

### With Opacity and Offset

```python
"final": Node(
    op_name="gfx:composite",
    params={
        "layers": [
            {
                "image": ref("background"),
                "id": "background",
            },
            {
                "image": ref("overlay"),
                "anchor": relative("background", "c@c", y=5),  # Center, shifted 5px down
                "id": "overlay",
                "opacity": Decimal("0.8"),  # 80% opacity
            },
        ],
    },
    deps=["background", "overlay"],
)
```

## **CEL Expression Support**

Builder functions (`absolute()`, `relative()`) return plain Python dicts. Invariant's `resolve_params()` (via `_resolve_value()`) recursively walks dicts and lists, resolving `ref()`, `cel()`, and `${...}` markers within nested structures. This means expressions embedded in anchor specs or layer dicts are evaluated during **Phase 1 (Context Resolution)** before the op executes, allowing dynamic positioning based on upstream artifact dimensions.

**Example with dynamic positioning:**
```python
{
    "image": ref("icon"),
    "anchor": relative("background", "c@c", y="${icon.height + 10}"),  # Position based on icon size
    "id": "icon",
}
```

## **Implementation**

The operation is implemented in [`src/invariant_gfx/ops/composite.py`](../src/invariant_gfx/ops/composite.py).

## **Related Operations**

* [`gfx:layout`](layout.md) - Content-sized arrangement engine for sequential flow layouts
* [`gfx:create_solid`](../architecture.md#gfxcreate_solid) - Generate solid color canvases for backgrounds

## **Note on Documentation Consistency**

After this rewrite, [architecture.md](../architecture.md) lines 238-257 still reference the old `dict[str, AnchorSpec]` API keyed by dependency ID. That section should be updated to match the list-based design documented here, but that update is out of scope for this specification document.

