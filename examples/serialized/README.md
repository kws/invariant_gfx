# Serialized Examples

## Square Button Badge

[`square_button_badge.json`](./square_button_badge.json) is a serialized graph
document for a square button/badge template. It declares `final` as its default
`output`, so the CLI can execute it without `--pick`:

- `gfx:create_solid` creates a 144x144 button background.
- `stdlib:coalesce` resolves optional `text`, `color`, `width`, and `height`
  params to graph-local defaults.
- `gfx:resolve_color` resolves a hex or named text color to an RGBA tuple.
- `gfx:render_text` renders the resolved text using `fit_width`.
- `gfx:composite` centers the fitted text on the background.

Run it with explicit nulls to select graph-local defaults:

```bash
uv run python -m invariant \
  examples/serialized/square_button_badge.json \
  --param text=null \
  --param color=null \
  --param width=null \
  --param height=null \
  --output output/square_button_badge.png
```

Override the context defaults from the CLI:

```bash
uv run python -m invariant \
  examples/serialized/square_button_badge.json \
  --param "text=My Button" \
  --param "color=#FF0000" \
  --param width=144 \
  --param height=72 \
  --output output/button.png
```

The CLI selects the `final` `ImageArtifact` and writes it as a PNG. Without
`--output`, the selected artifact is emitted as Invariant JSON. In Python, load
the same graph with `load_graph_document_from_dict()`, execute the returned
default output with a context such as `{"text": "SALE", "color": "gold",
"width": 144, "height": 72}`, or pass explicit `None` values to select
graph-local defaults, then save `results[output].image` as PNG.

For controller-style integrations, the graph can be encoded once as an
Invariant graph data URI and reused with query-string context:

```text
data:application/vnd.invariant.graph+json;base64,<encoded-square-button-badge>?text=SALE&color=gold&width=144&height=72
```

The encoded graph document is static and cacheable. The query string provides
per-render context values.
