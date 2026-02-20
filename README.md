# invariant_gfx

A deterministic, functional graphics pipeline built on **Invariant**. invariant_gfx allows developers to build complex visual assets (icons, badges, dynamic UI components, Stream Deck buttons, data visualizations) by plugging together reusable "pipeline parts" in a DAG-based system.

> **Note**: This project builds on [Invariant](https://github.com/kws/invariant/blob/main/README.md), a deterministic execution engine for DAGs. For information about Invariant's core concepts (DAG execution, caching, execution model, parameter markers, etc.), see the [upstream README](https://github.com/kws/invariant/blob/main/README.md) and [Invariant documentation](https://github.com/kws/invariant).

## Features

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

This example demonstrates graphics-specific operations. For details on Invariant's execution model, parameter markers (`ref()`, `cel()`, `${...}`), and context injection, see the [upstream README](https://github.com/kws/invariant/blob/main/README.md).

```python
from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import absolute, relative

# Register graphics ops
registry = OpRegistry()
register_core_ops(registry)  # Registers gfx:* ops

# Define the graph template (designed at 72px reference size)
graph = {
    # Render text with proportional sizing
    "text": Node(
        op_name="gfx:render_text",
        params={
            "text": "Hello",
            "font": "Geneva",
            "size": "${decimal(root.width) * decimal('14') / decimal('72')}",  # 14pt at 72px, scales proportionally
            "color": (255, 255, 255, 255),  # White RGBA
        },
        deps=["root"],
    ),
    # Create background (size from context)
    "background": Node(
        op_name="gfx:create_solid",
        params={
            "size": ("${root.width}", "${root.height}"),
            "color": (40, 40, 40, 255),  # Dark gray RGBA
        },
        deps=["root"],
    ),
    # Composite: center text on background
    "final": Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {
                    "image": ref("background"),
                    "id": "background",
                },
                {
                    "image": ref("text"),
                    "anchor": relative("background", "c@c"),
                    "id": "text",
                },
            ],
        },
        deps=["background", "text"],
    ),
}

# Execute the graph
store = MemoryStore()
executor = Executor(registry=registry, store=store)

# Render at 72x72 (text at 14pt)
results = executor.execute(graph, context={"root": {"width": 72, "height": 72}})
results["final"].image.save("output_72.png", format="PNG")

# Render at 144x144 (text scales to 28pt automatically)
results = executor.execute(graph, context={"root": {"width": 144, "height": 144}})
results["final"].image.save("output_144.png", format="PNG")
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

invariant_gfx uses Invariant's execution model. For details on the two-phase execution model (Context Resolution and Action Execution), see the [upstream documentation](https://github.com/kws/invariant).

For invariant_gfx-specific architecture documentation, see [docs/architecture.md](docs/architecture.md).

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
