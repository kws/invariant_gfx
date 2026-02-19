# invariant_gfx

A deterministic, functional graphics pipeline built on **Invariant**. invariant_gfx allows developers to build complex visual assets (icons, badges, dynamic UI components, Stream Deck buttons, data visualizations) by plugging together reusable "pipeline parts" in a DAG-based system.

Unlike traditional imperative rendering (where you draw lines on a mutable canvas), invariant_gfx is **functional**: every layer, mask, or composition is an immutable **Artifact** produced by a pure function.

## Features

- **Aggressive Caching**: Identical visual operations (rendering the same text, compositing the same layers) execute only once
- **Deduplication**: The same icon rendered at the same size is reused across all buttons
- **Reproducibility**: Bit-for-bit identical outputs across runs and architectures
- **Functional Rendering**: Immutable artifacts flow through pure function operations
- **Smart Layout**: Ops can inspect upstream artifact dimensions to calculate positions dynamically
- **Anchor-Based Composition**: Position layers relative to previously-placed named layers using `absolute()` and `relative()` builder functions
- **Content-Sized Layout**: Flow-based arrangement (row/column) with automatic sizing

## Relationship to Invariant

invariant_gfx is a **child project** of Invariant:

- **Invariant (Parent)**: Provides the DAG execution engine, caching infrastructure, and core protocols. Invariant has **NO image awareness**—it is domain-agnostic.
- **invariant_gfx (Child)**: Provides graphics-specific Ops (`gfx:render_text`, `gfx:composite`, `gfx:render_svg`, etc.) and Artifacts (`ImageArtifact`, `BlobArtifact`). All image/Pillow concerns live here.

invariant_gfx uses Invariant's `Executor` and store infrastructure directly—no wrapper class is needed.

## Op Standard Library

invariant_gfx provides a standard library of graphics operations, registered under the `gfx:` namespace:

### Group A: Sources (Data Ingestion)
- `gfx:resolve_resource`: Resolves bundled resources (icons, images) via JustMyResource (e.g., `"lucide:thermometer"`)
- `gfx:create_solid`: Generates solid color canvases (RGBA)
- `gfx:resolve_font`: Resolves font family names to font file bytes via JustMyType *(deferred — `gfx:render_text` handles font resolution implicitly)*

### Group B: Transformers (Rendering)
- `gfx:render_svg`: Converts SVG blobs into raster artifacts using cairosvg
- `gfx:render_text`: Creates tight-fitting "Text Pill" artifacts (supports string font names via JustMyType and direct `BlobArtifact` font injection)
- `gfx:resize`: Scales an `ImageArtifact` to target dimensions (LANCZOS resampling)

### Group C: Composition (Combiners)
- `gfx:composite`: Fixed-size composition engine with anchor-based positioning (`absolute()`, `relative()`)
- `gfx:layout`: Content-sized arrangement engine (row/column flow)

### Group D: Type Conversion (Casting)
- `gfx:blob_to_image`: Parses raw binary data (PNG, JPEG, WEBP) into `ImageArtifact`

For detailed Op specifications, see [docs/architecture.md](docs/architecture.md).

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd invariant_gfx

# Install dependencies
poetry install
```

**Note**: This project depends on a local development version of Invariant. The dependency is configured in `pyproject.toml` as a file path reference.

## Quick Start

```python
from decimal import Decimal

from invariant import Executor, Node
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import absolute, relative

# Register graphics ops
registry = OpRegistry()
register_core_ops(registry)  # Registers gfx:* ops

# Define the graph
graph = {
    # Render text
    "text": Node(
        op_name="gfx:render_text",
        params={
            "text": "Hello",
            "font": "Geneva",
            "size": Decimal("14"),
            "color": (255, 255, 255, 255),  # White RGBA
        },
        deps=[],
    ),
    # Create background
    "background": Node(
        op_name="gfx:create_solid",
        params={
            "size": (Decimal("72"), Decimal("72")),
            "color": (40, 40, 40, 255),  # Dark gray RGBA
        },
        deps=[],
    ),
    # Composite: center text on background
    "final": Node(
        op_name="gfx:composite",
        params={
            "layers": {
                "background": absolute(0, 0),  # First layer defines canvas
                "text": relative("background", "c,c"),  # Center on background
            },
        },
        deps=["background", "text"],
    ),
}

# Execute the graph
store = MemoryStore()
executor = Executor(registry=registry, store=store)
results = executor.execute(graph)

# Access result
final_image = results["final"].image  # PIL.Image (RGBA)
final_image.save("output.png", format="PNG")
```

For more complete examples, see:
- `examples/thermometer_button.py` — Icon + text + layout + composite pipeline
- `examples/text_badge.py` — Dynamic SVG resizing driven by text dimensions
- `examples/color_dashboard.py` — Multi-cell dashboard with nested layouts

For the full Thermometer pipeline and template + context pattern, see [docs/architecture.md](docs/architecture.md).

## Status

**Architecture**: Complete and documented

**Implementation**: V1 op library complete
- Artifact types (`ImageArtifact`, `BlobArtifact`): ✅ Implemented
- Anchor functions (`absolute()`, `relative()`): ✅ Implemented
- Op standard library (8 ops): ✅ Implemented
- `register_core_ops()` registration: ✅ Implemented
- Integration with JustMyType/JustMyResource: ✅ Implemented
- Unit tests (94 tests): ✅ All passing
- E2E tests (Use Cases 1 & 2): ✅ Passing
- E2E context injection (Use Case 3): ⏳ Placeholder

See [docs/status.md](docs/status.md) for detailed implementation status.

## Architecture

invariant_gfx uses Invariant's two-phase execution model:

1. **Phase 1: Context Resolution** - Builds input manifests for each node, calculates stable hashes
2. **Phase 2: Action Execution** - Executes operations or retrieves from cache

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

For AI agents working with this codebase, see [AGENTS.md](AGENTS.md).

## Development

```bash
# Run tests
poetry run pytest

# Run linting
poetry run ruff check src/ tests/

# Format code
poetry run ruff format src/ tests/
```

## License

MIT License - see [LICENSE](LICENSE) for details.
