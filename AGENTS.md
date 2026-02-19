# **AGENTS.md: Essential Information for AI Agents**

This document provides must-know information about the invariant_gfx system. For comprehensive details, see [docs/architecture.md](./docs/architecture.md).

## **What is invariant_gfx?**

invariant_gfx is a deterministic, DAG-based graphics engine built on **Invariant**. It allows developers to build complex visual assets (like Stream Deck buttons, dynamic badges, or data visualizations) by plugging together reusable "pipeline parts."

Unlike traditional imperative rendering (where you draw lines on a mutable canvas), invariant_gfx is **functional**: every layer, mask, or composition is an immutable **Artifact** produced by a pure function.

**Core Value:**
- **Aggressive Caching:** Identical visual operations (rendering the same text, compositing the same layers) execute only once
- **Deduplication:** The same icon rendered at the same size is reused across all buttons
- **Reproducibility:** Bit-for-bit identical outputs across runs and architectures
- **Smart Layout:** Ops can inspect upstream artifact dimensions to calculate positions dynamically

## **Relationship to Invariant (Parent-Child)**

invariant_gfx is a **child project** of Invariant. The relationship is:

- **Invariant (Parent):** Provides the DAG execution engine, caching infrastructure, and core protocols. Invariant has **NO image awareness**—it is domain-agnostic.
- **invariant_gfx (Child):** Provides graphics-specific Ops (render_text, composite, render_svg) and Artifacts (ImageArtifact, BlobArtifact). All image/Pillow concerns live here.

**Clear Boundary:**
- Invariant knows about `ICacheable`, `Node`, `Executor`, `OpRegistry`, `ArtifactStore`
- Invariant does NOT know about images, fonts, icons, or rendering
- invariant_gfx implements graphics Ops that return `ICacheable` artifacts
- invariant_gfx may extend Invariant's capabilities (e.g., Pipeline wrapper class) but keeps graphics concerns isolated

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
- If a node needs data (like a URL or temperature value), that data must be the output of an upstream **Identity Node**
- The graph is hermetic—you can visualize exactly where every piece of data comes from

## **Core Terminology**

| Term | Definition | Key Point |
| :---- | :---- | :---- |
| **ImageArtifact** | Universal visual primitive (PIL.Image in RGBA) | Implements ICacheable, exposes .width/.height |
| **BlobArtifact** | Container for raw binary resources (SVG, TTF, PNG bytes) | Used for fonts, icons, downloaded assets |
| **LayerSpec** | Specification for a layer in composite op | Contains ref, id, anchor, mode, opacity |
| **anchor()** | DSL helper function for positioning layers | Returns AnchorSpec for composite op |
| **Op Groups** | Categories of operations (Sources, Transformers, Compositors, Casting) | See architecture.md for full list |

## **The Op Standard Library**

invariant_gfx provides a standard library of graphics operations organized into groups:

### **Group A: Sources (Data Ingestion)**
- `resolve_resource`: Resolves bundled resources (icons, images) via JustMyResource
- `create_solid`: Generates solid color canvas

### **Group B: Transformers (Rendering)**
- `render_svg`: Converts SVG blobs into raster artifacts using cairosvg
- `render_text`: Creates tight-fitting "Text Pill" artifacts (uses JustMyType for font resolution)
- `resize`: Scales an ImageArtifact to target dimensions

### **Group C: Composition (Combiners)**
- `composite`: Fixed-size composition engine with anchor-based positioning
- `layout`: Content-sized arrangement engine (row/column flow)

### **Group D: Type Conversion (Casting)**
- `blob_to_image`: Parses raw binary data (PNG, JPEG, WEBP) into ImageArtifact

See [docs/architecture.md](./docs/architecture.md) for detailed specifications of each op.

## **Missing Upstream Features (Gaps in Invariant)**

After reviewing the actual Invariant codebase, the status is:

| Feature | Status | Notes |
| :---- | :---- | :---- |
| **Expression Evaluation** | **Not needed for v1** | Executor populates manifest with upstream artifacts keyed by dep node ID. Ops access results via `manifest["node_id"]`. |
| **Context Injection** | **Handled by Pipeline wrapper** | Pipeline class (in invariant_gfx) accepts context dict and creates identity nodes automatically. |
| **Pipeline Class** | **To be implemented in invariant_gfx** | Wraps Executor with context support and dual-cache (MemoryStore + DiskStore). |
| **List/Dict Cacheable Types** | **Partial** | `hash_value()` hashes lists/dicts recursively, but standalone `List`/`Dict` ICacheable types don't exist. **V1 workaround:** Pass layer specs as plain Python dicts/lists in params (they're only used in manifests, not stored as artifacts). |
| **Op Namespace Enforcement** | **Not needed for v1** | Convention-based namespacing is sufficient (core ops use bare names, extensions use `namespace:op_name`).

## **External Dependencies**

invariant_gfx depends on:

- **Invariant:** The parent DAG execution engine
- **Pillow (PIL):** Image manipulation and rendering
- **JustMyType:** Font discovery and resolution (see [github.com/kws/justmytype](https://github.com/kws/justmytype))
- **JustMyResource:** Icon/resource discovery (see [github.com/kws/justmyresource](https://github.com/kws/justmyresource))

## **Execution Model: Inherited from Invariant**

invariant_gfx uses Invariant's two-phase execution model:

### **Phase 1: Context Resolution (Graph → Manifest)**
1. Traverse DAG, resolve inputs for each Node
2. Recursively calculate `get_stable_hash()` for all inputs
3. Assemble canonical dictionary (sorted keys)
4. Output: **Manifest** → hash becomes **Digest** (cache key)

### **Phase 2: Action Execution (Manifest → Artifact)**
1. **Cache Lookup:** Check `ArtifactStore.exists(Digest)`
   - If True: Return stored Artifact, **skip Op execution**
2. **Execution:** If False, invoke `OpRegistry.get(op_name)(manifest)`
3. **Persistence:** Serialize and save Artifact to `ArtifactStore` under Digest

## **Implementation Status**

**Designed (Architecture Complete):**
- Op standard library specification
- Artifact types (ImageArtifact, BlobArtifact)
- Composite and layout algorithms
- anchor() DSL helper

**Not Yet Implemented:**
- Actual Op implementations
- ImageArtifact and BlobArtifact classes
- Pipeline wrapper class
- Integration with JustMyType/JustMyResource

## **For More Information**

See [docs/architecture.md](./docs/architecture.md) for:
- Detailed Op specifications
- LayerSpec and anchor() documentation
- Complete pipeline examples
- Design philosophy and influences

See [../invariant/AGENTS.md](../invariant/AGENTS.md) for:
- Core Invariant concepts and constraints
- ICacheable protocol details
- Execution model deep dive

