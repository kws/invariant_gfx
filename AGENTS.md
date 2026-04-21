# **AGENTS.md: Essential Information for AI Agents**

This document provides must-know information about the Invariant GFX system. For comprehensive details, see [docs/architecture.md](./docs/architecture.md).

## **What is Invariant GFX?**

Invariant GFX is a deterministic, DAG-based graphics engine built on **Invariant**. It allows developers to build complex visual assets (like Stream Deck buttons, dynamic badges, or data visualizations) by plugging together reusable "pipeline parts."

Unlike traditional imperative rendering (where you draw lines on a mutable canvas), Invariant GFX is **functional**: every layer, mask, or composition is an immutable **Artifact** produced by a pure function.

**Core Value:**
- **Aggressive Caching:** Identical visual operations (rendering the same text, compositing the same layers) execute only once
- **Deduplication:** The same icon rendered at the same size is reused across all buttons
- **Reproducibility:** Bit-for-bit identical outputs across runs and architectures
- **Smart Layout:** Ops can inspect upstream artifact dimensions to calculate positions dynamically

## **Relationship to Invariant (Parent-Child)**

Invariant GFX is a **child project** of Invariant. The relationship is:

- **Invariant (Parent):** Provides the DAG execution engine, caching infrastructure, and core protocols. Invariant has **NO image awareness**—it is domain-agnostic.
- **Invariant GFX (Child):** Provides graphics-specific Ops (render_text, composite, render_svg) and Artifacts (ImageArtifact, BlobArtifact). All image/Pillow concerns live here.

**Clear Boundary:**
- Invariant knows about `ICacheable`, `Node`, `Executor`, `OpRegistry`, `ArtifactStore`
- Invariant does NOT know about images, fonts, icons, or rendering
- Invariant GFX implements graphics Ops that return `ICacheable` artifacts
- Invariant GFX uses Invariant's Executor and ChainStore directly—no wrapper needed

## **Development Setup**

**This project uses uv for dependency management and testing.**

- **Run tests:** `uv run pytest tests/` or `uv run pytest tests/test_file.py::test_name`
- **Install dependencies:** `uv sync`
- **Run Python commands:** `uv run python ...`
- **DO NOT** use bare `python`, `pytest`, or `python -m pytest` — always use `uv run` first

## **Release process**

Same conventions as the parent project [Invariant](../invariant/AGENTS.md) (**Release process**): uv, hatchling, git tags, no in-repo changelog unless you add one later.

### **Version source of truth**

- **Distribution version:** `[project].version` in `pyproject.toml` (PyPI / `pip` name **`invariant-gfx`**; Python import package **`invariant_gfx`**).
- **Runtime `__version__`:** `src/invariant_gfx/__init__.py` reads `importlib.metadata.version("invariant-gfx")`, so it always matches the installed distribution.

### **`invariant-core` dependency**

GFX depends on **`invariant-core`** (see `dependencies` in `pyproject.toml`). If a release needs APIs or fixes from a newer Invariant, **ship `invariant-core` first**, bump the specifier here if the minimum version rises, then cut **`invariant-gfx`**.

### **Version strings (PEP 440)**

- **Shipping releases:** plain semver in `pyproject.toml`, e.g. `0.2.0` (no `v` prefix in the file).
- **Between releases:** a **development release**, e.g. `0.3.0.dev0`, until the next stable cut.

### **`uv.lock` after a version change (workspace package)**

`invariant-gfx` is the editable workspace root. After you edit **`[project].version`** in `pyproject.toml`, run:

```bash
uv lock --refresh
```

**Why not plain `uv lock`?** A normal resolve can leave the `[[package]] name = "invariant-gfx"` stanza in `uv.lock` on the **previous** version until the lock is refreshed. **`uv lock --refresh`** forces the lockfile to match (look for output like `Updated invariant-gfx v0.2.0 -> v0.3.0.dev0`). Commit `uv.lock` together with `pyproject.toml`.

### **Cutting a stable release**

1. **Branch / mainline:** finish the work to ship; ensure **`uv run pytest tests/`** passes.
2. **Release commit:** set `version = "X.Y.Z"` in `pyproject.toml`, run **`uv lock --refresh`**, commit both files.
   - **Commit title:** `chore: release vX.Y.Z` (include `v` in the title).
   - **Commit body:** user-facing release notes (bullets). Use the git message as the canonical summary unless you add `CHANGELOG.md`.
3. **Tag:** lightweight (or annotated) git tag **`vX.Y.Z`** on that commit.
4. **Build artifacts for PyPI:** After the post-release dev bump, **`uv build` on `main` produces dev-tagged wheels**. For **`invariant_gfx-X.Y.Z-*.whl`** and **`invariant_gfx-X.Y.Z.tar.gz`**, build from the release tag:

   ```bash
   git checkout "vX.Y.Z"
   uv build
   git checkout -
   ```

5. **Publish (manual):** upload `dist/*` for **`invariant-gfx`** (no publish workflow in-repo unless you add one).

### **Immediately after the release**

Separate commit: bump to the next dev line (e.g. **`chore: bump to development release 0.3.0.dev0`**), set `version` in `pyproject.toml`, run **`uv lock --refresh`**, commit both files. The stable tag should point only at the stable commit, not the dev bump.

### **Tag and version checklist**

| Step | Check |
| :--- | :--- |
| `pyproject.toml` | `version` matches intended PEP 440 stable or dev string |
| `uv.lock` | After every version edit: **`uv lock --refresh`**, then confirm `invariant-gfx` in `uv.lock` matches `pyproject.toml` |
| `invariant-core` | Lower bound in `dependencies` is still correct for this release |
| Git tag | **`vX.Y.Z`** matches the semver in `pyproject.toml` on the release commit |
| `dist/` for upload | Built from **`vX.Y.Z`** (or that commit), not from `main` on a `.dev` version |

## **Critical Constraints (MUST FOLLOW)**

All constraints from Invariant apply, plus graphics-specific rules:

### **1. Immutability Contract (Inherited)**
- Once an **Artifact** is generated, it is **frozen**
- Downstream nodes **cannot modify** upstream artifacts
- Must consume and produce a **new** artifact

### **2. Determinism Contract (Inherited)**
- An **Op** must rely **only** on data in its **Input Manifest**
- **FORBIDDEN:** Global state, `time.now()`, `random.random()` inside Ops
- Exception: These values can be passed as explicit inputs from graph root

### **3. Strict Numeric Policy (Inherited)**
- **FORBIDDEN:** Native `float` types in cacheable data
- **REASON:** IEEE 754 floats are non-deterministic across architectures
- **SOLUTION:** Use `decimal.Decimal` (canonicalized to string) or integer ratios
- **Graphics Note:** All layout inputs (offsets, font sizes, opacity) use `Decimal` or `int`

### **4. Image Format Standardization**
- All images are normalized to **RGBA** mode (PIL.Image)
- Serialization uses canonical **PNG** (Level 1 compression, metadata stripped)
- Artifact identity is SHA-256 of the PNG bytes

### **5. Explicit Data Flow (No Global Context)**
- There is no "Global Context" or "Environment Variables"
- If a node needs data (like a URL or temperature value), that data is either the output of an upstream node in the graph, or an external dependency provided via `context` when executing the graph
- The graph is hermetic—you can visualize exactly where every piece of data comes from

## **Core Terminology**

| Term | Definition | Key Point |
| :---- | :---- | :---- |
| **ImageArtifact** | Universal visual primitive (PIL.Image in RGBA) | Implements ICacheable, exposes .width/.height |
| **BlobArtifact** | Container for raw binary resources (SVG, TTF, PNG bytes) | Used for fonts, icons, downloaded assets |
| **Anchor Functions** | Builder functions for layer positioning in composite op | `absolute(x, y)` for pixel coordinates, `relative(parent, align, x, y)` for parent-relative positioning |
| **Op Groups** | Categories of operations (Sources, Transformers, Compositors, Casting) | See architecture.md for full list |

## **The Op Standard Library**

Invariant GFX provides a standard library of graphics operations organized into groups:

### **Group A: Sources (Data Ingestion)**
- `gfx:resolve_resource`: Resolves bundled resources (icons, images) via JustMyResource
- `gfx:create_solid`: Generates solid color canvas

### **Group B: Transformers (Rendering)**
- `gfx:render_svg`: Converts SVG blobs into raster artifacts using cairosvg. Use `invariant_gfx.shapes` (rect, rounded_rect, circle, ellipse, line, polygon, arc, diamond, parallelogram, hexagon, arrow) to build SVG strings for fit-to-content or literal dimensions.
- `gfx:render_text`: Creates tight-fitting "Text Pill" artifacts (uses JustMyType for font resolution)
- `gfx:resize`: Scales an ImageArtifact (width/height/scale; scale mutually exclusive with width/height)
- `gfx:rotate`: Rotates an ImageArtifact by angle in degrees
- `gfx:flip`: Flips an ImageArtifact horizontally and/or vertically
- `gfx:transform`: Wraps PIL Image.transform (extent, affine, perspective, quad). Use quad for reflection perspective.
- `gfx:thumbnail`: Resizes to fit bounding box with aspect preservation (contain/cover modes)
- `gfx:crop_to_content`: Trims transparent pixels to content bounding box
- `gfx:grayscale`: Converts to grayscale, preserves alpha
- `gfx:crop_region`: Crops by (x, y, width, height)
- `gfx:gradient_opacity`: Linear gradient on alpha (angle in degrees, start/end opacity)

### **Group C: Composition (Combiners)**
- `gfx:composite`: Fixed-size composition engine with anchor-based positioning. Uses function-based DSL (`absolute()`, `relative()`) with parent references for layer positioning. Layers specified as list of dicts with `image`, `anchor`, `id`. See [docs/composite.md](./docs/composite.md).
- `gfx:layout`: Content-sized arrangement engine (row/column flow)

### **Group D: Type Conversion (Casting)**
- `gfx:blob_to_image`: Parses raw binary data (PNG, JPEG, WEBP) into ImageArtifact

### **Group E: Color & Effect Primitives**
- `gfx:brightness_contrast`: Adjusts brightness and contrast by factor
- `gfx:tint`: Multiply-blends color onto image (preserves luminance; differs from colorize)

See [docs/architecture.md](./docs/architecture.md) for detailed specifications of each op.

## **Upstream (Invariant)**

For cacheable types, expression syntax, and execution model, see [Invariant](https://github.com/kws/invariant).

## **External Dependencies**

Invariant GFX depends on:

- **Invariant:** The parent DAG execution engine
- **Pillow (PIL):** Image manipulation and rendering
- **JustMyType:** Font discovery and resolution (see [github.com/kws/justmytype](https://github.com/kws/justmytype))
- **JustMyResource:** Icon/resource discovery (see [github.com/kws/justmyresource](https://github.com/kws/justmyresource))

## **Execution Model: Inherited from Invariant**

Invariant GFX uses Invariant's two-phase execution model:

### **Phase 1: Context Resolution (Graph → Manifest)**
1. Traverse DAG, resolve inputs for each Node
2. Recursively calculate `get_stable_hash()` for all inputs
3. Assemble canonical dictionary (sorted keys)
4. Output: **Manifest** → hash becomes **Digest** (cache key)

### **Phase 2: Action Execution (Manifest → Artifact)**
1. **Cache Lookup:** Check `ArtifactStore.exists(op_name, Digest)`
   - If True: Return stored Artifact, **skip Op execution**
2. **Execution:** If False, invoke `OpRegistry.get(op_name)(manifest)`
3. **Persistence:** Serialize and save Artifact to `ArtifactStore` under (op_name, Digest)

## **Implementation Status**

Core ops, artifacts, effects, and dependency integrations (JustMyType, JustMyResource) are implemented.

## **Cache and MemoryStore**

**MemoryStore default:** Invariant's `MemoryStore` defaults to `cache="lru"` (least-recently-used) with `max_size=1000`. For graphics pipelines, **LFU (least-frequently-used)** is often a better fit: shared icons, fonts, and intermediate compositions are reused across many outputs, so evicting by frequency rather than recency improves hit rates.

```python
from invariant.store.memory import MemoryStore
from invariant.store.chain import ChainStore
from invariant.store.disk import DiskStore

# Recommended for graphics: LFU L1 cache
store = ChainStore(
    l1=MemoryStore(cache="lfu", max_size=2000),
    l2=DiskStore(),
)
```

**Ephemeral nodes (`cache=False`):** Nodes that render frequently-changing inputs (e.g. current time, live data) and are rarely reused should set `cache=False`. The executor skips cache lookup and never stores the result—the op runs every time. Use for nodes whose outputs change often and would pollute the cache.

```python
Node(
    op_name="gfx:render_text",
    params={"text": "${root.time}", "size": 12, ...},
    deps=["root"],
    cache=False,  # Time changes every second; don't cache
)
```

## **Graph Serialization**

GFX graphs use Invariant's JSON wire format. See [../invariant/docs/serialization.md](../invariant/docs/serialization.md) for the normative spec.

**When adding new artifacts:**

- All artifacts must implement `ICacheable` (required for artifact storage and manifest hashing).
- For graph params: literal ICacheable values in params are encoded as `$icacheable` with either `payload_b64` (binary) or `value` (if the type implements `IJsonRepresentable`).
- **Do not add `IJsonRepresentable`** for binary-heavy types (ImageArtifact, BlobArtifact). The main content (pixels, raw bytes) is never human-readable; `payload_b64` is sufficient. Adding `to_json_value`/`from_json_value` would only expose metadata (e.g. width/height, content_type) while the payload stays base64—the maintenance cost outweighs the marginal benefit.
- Consider `IJsonRepresentable` only for small, structured param types (e.g. effect config objects) where the JSON would be genuinely readable.

## **For More Information**

See [docs/README.md](./docs/README.md) for the documentation index.

See [docs/architecture.md](./docs/architecture.md) for:
- Detailed Op specifications
- LayerSpec documentation
- Design philosophy and influences

See [docs/reference_pipelines.md](./docs/reference_pipelines.md) for complete pipeline examples (Layered Badge, Content Flow, Template Reuse).

See [../invariant/AGENTS.md](../invariant/AGENTS.md) for:
- Core Invariant concepts and constraints
- ICacheable protocol details
- Execution model deep dive
- **Release process for `invariant-core`** (this file documents **`invariant-gfx`** releases under **Release process** above)

See [../invariant/docs/serialization.md](../invariant/docs/serialization.md) for:
- Graph JSON wire format (Node, SubGraphNode, ref, cel, $icacheable)

