# Invariant GFX

A deterministic, functional graphics pipeline built on **Invariant**. Invariant GFX allows developers to build complex visual assets (icons, badges, dynamic UI components, Stream Deck buttons, data visualizations) by plugging together reusable "pipeline parts" in a DAG-based system.

> **Note**: This project builds on [Invariant](https://github.com/kws/invariant/blob/main/README.md), a deterministic execution engine for DAGs. For information about Invariant's core concepts (DAG execution, caching, execution model, parameter markers, etc.), see the [upstream README](https://github.com/kws/invariant/blob/main/README.md) and [Invariant documentation](https://github.com/kws/invariant).

## What is Invariant GFX?

Invariant GFX gives you aggressive caching and deduplication: identical visual operations run once and are reused. Outputs are bit-for-bit reproducible, and layout can be driven by upstream artifact dimensions so the same graph scales across sizes.

**High-level features:**

- **Smart layout** — Ops inspect upstream artifact dimensions to calculate positions dynamically.
- **Anchor-based composition** — Position layers with `absolute()` and `relative()` builder functions, referencing previously-placed named layers.
- **Content-sized layout** — Row/column flow with automatic sizing.
- **Effects as subgraphs** — Filter primitives (blur, alpha, morphology) are composed into effect recipes (e.g. drop shadow) via `SubGraphNode`. See [docs/effects.md](docs/effects.md).
- **Deterministic and cacheable** — No floats in cacheable data; all layout uses `Decimal` or integers.

**Relationship to Invariant:** Invariant GFX is a child project of Invariant. The parent provides the DAG execution engine, caching, and core protocols (no image awareness). Invariant GFX provides graphics ops (`gfx:render_text`, `gfx:composite`, `gfx:render_svg`, etc.) and artifacts (`ImageArtifact`, `BlobArtifact`). It uses Invariant's Executor and store directly—no wrapper.

## Get started

### Installation

```bash
# Clone the repository
git clone https://github.com/kws/invariant-gfx
cd invariant-gfx

# Install dependencies
uv sync
```

This project depends on a local development version of Invariant; the dependency is configured in `pyproject.toml` as a file path reference.

### Quick Start

Minimal example: text on a solid background, with proportional font sizing (14pt at 72px reference). Run with `uv run python -c "..."` or adapt from [examples/quick_start.py](examples/quick_start.py).

```python
from decimal import Decimal
from invariant import Executor, Node, ref
from invariant.registry import OpRegistry
from invariant.store.memory import MemoryStore

from invariant_gfx import register_core_ops
from invariant_gfx.anchors import relative

registry = OpRegistry()
register_core_ops(registry)
store = MemoryStore()
executor = Executor(registry=registry, store=store)

size = 72
font_size = int(Decimal(str(size)) * Decimal("14") / Decimal("72"))

graph = {
    "text": Node(
        op_name="gfx:render_text",
        params={
            "text": "Hello",
            "font": "Geneva",
            "size": font_size,
            "color": (255, 255, 255, 255),
        },
        deps=[],
    ),
    "background": Node(
        op_name="gfx:create_solid",
        params={
            "size": (size, size),
            "color": (40, 40, 40, 255),
        },
        deps=[],
    ),
    "final": Node(
        op_name="gfx:composite",
        params={
            "layers": [
                {"image": ref("background"), "id": "background"},
                {"image": ref("text"), "anchor": relative("background", "c@c"), "id": "text"},
            ],
        },
        deps=["background", "text"],
    ),
}

results = executor.execute(graph)
results["final"].image.save("output.png", format="PNG")
```

Proportional sizing can also be driven by **context + CEL** when using the template+context pattern; see [docs/architecture.md](docs/architecture.md).

### Examples

- `examples/quick_start.py` — Minimal text-on-background with proportional sizing.
- `examples/thermometer_button.py` — Icon + text + layout + composite pipeline.
- `examples/text_badge.py` — Dynamic SVG resizing driven by text dimensions.
- `examples/color_dashboard.py` — Multi-cell dashboard with nested layouts.
- `examples/text_drop_shadow.py` — Text with drop-shadow recipe (effect subgraph).

**Where to go next:** For full op specs, pipeline examples, and the template+context pattern, see [docs/architecture.md](docs/architecture.md). For effects and filter primitives, see [docs/effects.md](docs/effects.md).

### Reference

Invariant GFX provides graphics ops under the `gfx:` namespace: **sources** (resolve_resource, create_solid), **transformers** (render_svg, render_text, resize), **composition** (composite, layout), **casting** (blob_to_image), and **effects** (extract_alpha, blur, colorize, translate, pad, etc.). See [docs/architecture.md](docs/architecture.md) and [docs/effects.md](docs/effects.md) for the full list and specifications.

## Contributing

```bash
# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Format
uv run ruff format src/ tests/
```

For constraints, terminology, and implementation context, see [AGENTS.md](AGENTS.md). Implementation status and test coverage are documented in [docs/status.md](docs/status.md).

For execution model and GFX-specific design, see [docs/architecture.md](docs/architecture.md).

## License

MIT License — see [LICENSE](LICENSE) for details.
