# **gfx:layout Operation Specification**

Content-sized arrangement engine. Arranges items in a flow (row or column) when the output size is not known upfront.

## **Inputs**

* `direction`: `"row"` or `"column"` (main axis flow direction).
* `align`: Cross-axis alignment using `"s"` (start), `"c"` (center), or `"e"` (end).
* `gap`: `Decimal` (spacing between items in pixels).
* `items`: `list[ImageArtifact]` — ordered list of images to arrange. In node params, each item is typically provided via `ref("dep_name")`, which resolves to the upstream `ImageArtifact` during **Phase 1 (Context Resolution)**. The op receives the resolved artifacts, not the `ref()` markers.

## **Output**

`ImageArtifact` sized to the tight bounding box of the arranged items (RGBA mode).

## **Behavior**

### **Row Direction**

When `direction="row"`:
* Items are arranged horizontally from left to right
* **Main axis (width):** Sum of all item widths + gaps between items
* **Cross axis (height):** Maximum of all item heights
* Items are aligned on the cross-axis according to the `align` parameter

### **Column Direction**

When `direction="column"`:
* Items are arranged vertically from top to bottom
* **Main axis (height):** Sum of all item heights + gaps between items
* **Cross axis (width):** Maximum of all item widths
* Items are aligned on the cross-axis according to the `align` parameter

### **Cross-Axis Alignment**

The `align` parameter controls how items are positioned on the cross-axis:
* `"s"` (start): Align to the start of the cross-axis (top for column, left for row)
* `"c"` (center): Center items on the cross-axis
* `"e"` (end): Align to the end of the cross-axis (bottom for column, right for row)

## **Examples**

### Row Layout

Horizontal arrangement of three items:

```python
from invariant import ref

"row_layout": Node(
    op_name="gfx:layout",
    params={
        "direction": "row",
        "align": "c",  # Center on cross-axis (vertical)
        "gap": Decimal("5"),
        "items": [ref("icon"), ref("text"), ref("badge")],
    },
    deps=["icon", "text", "badge"],
)
```

**Output dimensions:**
* Width = icon.width + 5 + text.width + 5 + badge.width
* Height = max(icon.height, text.height, badge.height)

### Column Layout

Vertical arrangement of icon and text:

```python
from invariant import ref

"content": Node(
    op_name="gfx:layout",
    params={
        "direction": "column",
        "align": "c",  # Center on cross-axis (horizontal)
        "gap": Decimal("5"),
        "items": [ref("icon"), ref("text")],
    },
    deps=["icon", "text"],
)
```

**Output dimensions:**
* Width = max(icon.width, text.width)
* Height = icon.height + 5 + text.height

## **Use Cases**

* Arranging icon + text vertically before compositing onto a fixed-size background
* Creating horizontal button bars with multiple elements
* Building content-sized containers that will later be positioned using `gfx:composite`
* Arranging multiple elements in a flow without needing precise pixel coordinates

## **Implementation**

The operation is implemented in [`src/invariant_gfx/ops/layout.py`](../src/invariant_gfx/ops/layout.py).

## **Related Operations**

* [`gfx:composite`](composite.md) - Fixed-size composition engine with anchor-based positioning
* [`gfx:create_solid`](../architecture.md#gfxcreate_solid) - Generate solid color canvases

